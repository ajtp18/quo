from typing import Dict, List, Any
from fastapi import HTTPException
import httpx
import json
from redis import asyncio as aioredis
from app.core.config import settings
from functools import lru_cache
from datetime import datetime, timedelta
from .link_factory import LinkPayloadFactory

class BelvoService:
    """Service for handling Belvo API interactions"""
    
    def __init__(self):
        self._auth = (settings.BELVO_SECRET_ID, settings.BELVO_SECRET_PASSWORD)
        self._base_url = settings.BELVO_API_URL
        self._redis = None

    async def _get_redis(self):
        if not self._redis:
            self._redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to Belvo API"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self._base_url}/api/{endpoint}"
                response = await client.request(
                    method=method,
                    url=url,
                    auth=self._auth,
                    **kwargs
                )
                
                if response.status_code >= 400:
                    error_data = response.json()
                    if isinstance(error_data, list):
                        error_detail = error_data[0].get('message', str(error_data))
                    else:
                        error_detail = error_data.get('detail', str(error_data))
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_detail
                    )
                    
                return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_institutions(self) -> List[Dict]:
        """Get list of available institutions"""
        try:
            response = await self._make_request("GET", "institutions/")
            
            return response.get("results", [])
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_accounts(self, link_id: str) -> List[Dict]:
        """Get accounts for a link with caching"""
        redis = await self._get_redis()
        cache_key = f"accounts:{link_id}"
        
        cached = await redis.get(cache_key)
        if cached:
            cached_data = json.loads(cached)
            if cached_data and len(cached_data) > 0:
                return self._transform_accounts(cached_data, link_id)
        
        try:
            await self._make_request(
                "POST",
                "accounts/",
                json={"link": link_id, "save_data": True}
            )
            
            response = await self._make_request(
                "GET", 
                "accounts/",
                params={"link": link_id}
            )
            accounts = response.get("results", [])
            
            if accounts and len(accounts) > 0:
                transformed_accounts = self._transform_accounts(accounts, link_id)
                await redis.set(cache_key, json.dumps(accounts), ex=300)
                return transformed_accounts
            
            return []
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _transform_accounts(self, accounts: List[Dict], link_id: str) -> List[Dict]:
        """Transform accounts to match schema"""
        for account in accounts:
            if "institution" in account:
                account["institution"]["id"] = 0
                account["institution"]["icon_logo"] = ""
                account["institution"]["link_id"] = link_id
        return accounts

    async def get_transactions(self, link_id: str, account_id: str, 
                             date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get transactions for an account with caching"""
        redis = await self._get_redis()
        cache_key = f"transactions:{link_id}:{account_id}"
        
        cached = await redis.get(cache_key)
        if cached:
            cached_data = json.loads(cached)
            if cached_data and len(cached_data) > 0:
                return cached_data
        
        try:
            # Calculate default dates if not provided
            if not date_from or not date_to:
                today = datetime.now()
                default_from = (today - timedelta(days=90)).strftime("%Y-%m-%d")
                default_to = today.strftime("%Y-%m-%d")
                date_from = date_from or default_from
                date_to = date_to or default_to

            # register transactions
            await self._make_request(
                "POST",
                "transactions/",
                json={
                    "link": link_id,
                    "save_data": True,
                    "date_from": date_from,
                    "date_to": date_to
                }
            )
            
            # get transactions from Belvo
            response = await self._make_request(
                "GET", 
                "transactions/",
                params={
                    "link": link_id,
                    "account": account_id,
                    "page_size": 100
                }
            )
            
            transactions = response.get("results", [])
            
            if transactions and len(transactions) > 0:
                await redis.set(cache_key, json.dumps(transactions), ex=300)
            
            return transactions
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_link(
        self, 
        institution: str, 
        credentials: Dict[str, Any]
    ) -> dict:
        """Create a link with a bank"""
        try:
            institutions = await self.get_institutions()
            valid_institutions = [inst["name"] for inst in institutions]
            
            if institution not in valid_institutions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid institution. Valid options are: {', '.join(valid_institutions)}"
                )
            
            payload = LinkPayloadFactory.create_payload(
                institution=institution,
                credentials=credentials,
                institutions_list=institutions
            )
            
            response = await self._make_request(
                "POST",
                "links/",
                json=payload
            )
            
            if isinstance(response, dict) and "results" in response:
                return {
                    "count": response.get("count", 0),
                    "next": response.get("next"),
                    "previous": response.get("previous"),
                    "results": response.get("results", [])
                }
            
            return {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [response]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_account_details(self, link_id: str, account_id: str) -> Dict:
        """Get specific account details"""
        try:
            response = await self._make_request(
                "GET", 
                f"accounts/{account_id}/",
                params={"link": link_id}
            )
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@lru_cache()
def get_belvo_service() -> BelvoService:
    """Get singleton instance of BelvoService"""
    return BelvoService() 