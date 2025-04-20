from typing import Dict, Any
from enum import Enum
from app.core.config import settings


class InstitutionType(Enum):
    BANK = "bank"
    EMPLOYMENT = "employment"
    FISCAL = "fiscal"


class UsernameType(Enum):
    """Username types supported by Belvo"""
    CPF = "999" 
    CNPJ = "003"


class LinkPayloadFactory:
    """
    Factory to create specific payloads based on the institution type
    """
    
    # institutions that require username_type
    INSTITUTIONS_WITH_TYPE = {
        "ironbank_br_business": ["999", "003"],
        "ironbank_br_retail": ["999", "003"],
    }
    
    DEFAULT_CREDENTIALS = {
        "bank": {
            "username": settings.BANK_DEFAULT_USERNAME,
            "password": settings.BANK_DEFAULT_PASSWORD
        },
        "employment": {
            "document_id": settings.EMPLOYMENT_DEFAULT_DOCUMENT,
            "email": settings.EMPLOYMENT_DEFAULT_EMAIL,
            "password": settings.EMPLOYMENT_DEFAULT_PASSWORD
        },
        "fiscal": {
            "rfc": settings.FISCAL_DEFAULT_RFC,
            "password": settings.FISCAL_DEFAULT_PASSWORD
        }
    }
    
    @staticmethod
    def get_institution_type(institution_name: str, institutions_list: list) -> str:
        """
        Get the institution type based on its name
        """
        for inst in institutions_list:
            if inst["name"] == institution_name:
                return inst["type"]
        return "bank"
    
    @staticmethod
    def needs_username_type(institution: str) -> list:
        """
        Check if the institution requires username_type and returns the allowed types
        """
        return LinkPayloadFactory.INSTITUTIONS_WITH_TYPE.get(institution, [])
    
    @staticmethod
    def create_payload(
        institution: str,
        credentials: Dict[str, Any],
        institutions_list: list,
        access_mode: str = "single"
    ) -> dict:
        """
        Create the specific payload based on the institution type
        """
        institution_type = LinkPayloadFactory.get_institution_type(institution, institutions_list)
        
        base_payload = {
            "institution": institution,
            "access_mode": access_mode
        }
        
        # Check if it needs username_type
        allowed_types = LinkPayloadFactory.needs_username_type(institution)
        if allowed_types:
            # By default we use CPF (999) if not specified
            username_type = credentials.get("username_type", UsernameType.CPF.value)
            if username_type not in allowed_types:
                raise ValueError(f"Invalid username_type. Allowed types: {', '.join(allowed_types)}")
            base_payload["username_type"] = username_type
        
        if institution_type == InstitutionType.BANK.value:
            return {
                **base_payload,
                "username": credentials.get("username"),
                "password": credentials.get("password")
            }
            
        elif institution_type == InstitutionType.EMPLOYMENT.value:
            return {
                **base_payload,
                "username": credentials.get("document_id"),
                "username2": credentials.get("email"),
                "password": credentials.get("password")
            }
            
        elif institution_type == InstitutionType.FISCAL.value:
            return {
                **base_payload,
                "username": credentials.get("rfc"),
                "password": credentials.get("password"),
                "username2": credentials.get("email", None)
            }
            
        return base_payload 