from fastapi import APIRouter, Depends, HTTPException, Path
from app.api.deps import get_current_user
from app.services.belvo_service import get_belvo_service, BelvoService
from app.schemas.belvo import (
    Institution, 
    Account, 
    Transaction, 
    CalculatedKPI,
    LinkCreate, 
    Link, 
    TransactionResponse,
    LinkResponse,
    LinkRequest
)
from typing import List
from decimal import Decimal
from uuid import UUID

router = APIRouter()

@router.get("/institutions", response_model=List[Institution])
async def list_institutions(_=Depends(get_current_user)):
    """List available banking institutions"""
    try:
        service = get_belvo_service()
        institutions = await service.get_institutions()
        return institutions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{link_id}/accounts", response_model=List[Account])
async def list_accounts(link_id: str, _=Depends(get_current_user)):
    """List accounts for a link"""
    try:
        service = get_belvo_service()
        return await service.get_accounts(link_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )

@router.get("/{link_id}/accounts/{account_id}/transactions", response_model=TransactionResponse)
async def list_transactions(
    link_id: str = Path(..., description="Link ID"),
    account_id: UUID = Path(..., description="Account ID"),
    date_from: str = None,
    date_to: str = None,
    _=Depends(get_current_user)
):
    """List transactions and balance for an account"""
    try:
        service = get_belvo_service()
        
        # Obtener datos en paralelo
        transactions = await service.get_transactions(
            link_id, 
            str(account_id),
            date_from=date_from,
            date_to=date_to
        )
        
        # Calcular balance
        total_income = Decimal(0)
        total_expenses = Decimal(0)
        
        for transaction in transactions:
            amount = Decimal(str(transaction["amount"]))
            if transaction["type"] == "INFLOW":
                total_income += amount
            else:
                total_expenses += amount
                
        kpi = CalculatedKPI(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=total_income - total_expenses
        )
        
        # Obtener info de la cuenta
        account_info = await service.get_account_details(link_id, str(account_id))
        
        return TransactionResponse(
            transactions=transactions,
            kpi=kpi,
            account_info=account_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{link_id}/accounts/{account_id}/balance", response_model=CalculatedKPI)
async def get_balance(
    link_id: str = Path(..., description="Link ID"),
    account_id: UUID = Path(..., description="Account ID"),
    _=Depends(get_current_user)
):
    """Get balance for an account"""
    try:
        service = get_belvo_service()
        transactions = await service.get_transactions(link_id, str(account_id))
        
        total_income = Decimal(0)
        total_expenses = Decimal(0)
        
        for transaction in transactions:
            amount = Decimal(str(transaction["amount"]))
            if transaction["type"] == "INFLOW":
                total_income += amount
            else:
                total_expenses += amount
        
        return CalculatedKPI(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=total_income - total_expenses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/links/")
async def create_link(
    request: LinkRequest,
    belvo_service: BelvoService = Depends(get_belvo_service)
) -> dict:
    """
    Crea un nuevo link con una institución financiera
    """
    return await belvo_service.create_link(
        institution=request.institution,
        credentials=request.credentials
    )

@router.get("/links/{link_id}/status")
async def check_link_status(link_id: str, _=Depends(get_current_user)):
    """Check if link is ready"""
    try:
        service = get_belvo_service()
        response = await service._make_request(
            "GET",
            f"links/{link_id}/",
        )
        
        if response.get("status") == "valid":
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=400, detail="Link not ready")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 