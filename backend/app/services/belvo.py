from typing import Dict, List
import httpx
from app.core.config import settings

class BelvoClient:
    """Belvo API client"""
    
    def __init__(self):
        self.base_url = settings.BELVO_API_URL
        self.auth = (settings.BELVO_SECRET_ID, settings.BELVO_SECRET_PASSWORD)
        
    async def get_institutions(self) -> List[Dict]:
        """Get list of available institutions"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/institutions/",
                auth=self.auth
            )
            response.raise_for_status()
            return response.json()

    async def get_accounts(self, link_id: str) -> List[Dict]:
        """Get accounts for a link"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/accounts/",
                auth=self.auth,
                params={"link": link_id}
            )
            response.raise_for_status()
            return response.json()

    async def get_transactions(self, link_id: str, account_id: str) -> List[Dict]:
        """Get transactions for an account"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/transactions/",
                auth=self.auth,
                params={
                    "link": link_id,
                    "account": account_id
                }
            )
            response.raise_for_status()
            return response.json() 