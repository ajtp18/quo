from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime

class Institution(BaseModel):
    name: str
    type: str
    id: int | None = None
    link_id: str | None = None
    icon_logo: str | None = None

class AccountBalance(BaseModel):
    current: float
    available: float

class CalculatedKPI(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal

class Account(BaseModel):
    id: str
    link: str
    institution: Institution
    name: str
    type: str
    agency: str | None = None
    number: str | None = None
    balance: AccountBalance
    category: str
    currency: str
    created_at: datetime
    collected_at: datetime
    
    class Config:
        from_attributes = True

class TransactionMerchant(BaseModel):
    logo: Optional[str] = None
    website: Optional[str] = None
    merchant_name: Optional[str] = None

class TransactionAccount(BaseModel):
    id: str
    link: str
    institution: Institution
    name: str
    type: str
    agency: str | None = None
    number: str | None = None
    balance: AccountBalance
    category: str
    currency: str
    collected_at: datetime
    created_at: datetime

class Transaction(BaseModel):
    id: str
    account: TransactionAccount
    created_at: datetime
    collected_at: datetime
    value_date: str
    amount: float
    currency: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    type: str
    status: str
    merchant: Optional[TransactionMerchant] = None
    
    class Config:
        from_attributes = True

class BankCredentials(BaseModel):
    """Credenciales para instituciones bancarias"""
    username: str
    password: str
    username_type: Optional[str] = None

class EmploymentCredentials(BaseModel):
    """Credenciales para instituciones de empleo (IMSS, etc)"""
    document_id: str = Field(..., description="NSS o documento de identidad")
    email: str
    password: str

class FiscalCredentials(BaseModel):
    """Credenciales para instituciones fiscales (SAT, etc)"""
    rfc: str
    password: str
    email: Optional[str] = None

class LinkRequest(BaseModel):
    """Request para crear un link"""
    institution: str
    credentials: dict

class LinkCreate(BaseModel):
    institution: str
    username: str | None = None
    password: str | None = None

class Link(BaseModel):
    id: str
    institution: str
    access_mode: str
    status: str
    refresh_rate: Optional[str] = None
    created_by: str
    last_accessed_at: datetime
    external_id: Optional[str] = None
    created_at: datetime
    institution_user_id: str
    credentials_storage: str
    stale_in: Optional[str] = None
    fetch_resources: List[str] = []

class LinkResponse(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Link]

class TransactionResponse(BaseModel):
    transactions: List[Transaction]
    kpi: CalculatedKPI
    account_info: Account 