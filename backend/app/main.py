from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db
from app.api.v1 import auth, users, banks
from app.api.middleware.auth import AuthMiddleware
from app.api.middleware.cache import CacheMiddleware
from app.api.middleware.error import ErrorMiddleware
import logging

# Configurar logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development
        "https://*.onrender.com",  # Render domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CacheMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(ErrorMiddleware)

@app.on_event("startup")
async def startup_event():
    await init_db()

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(banks.router, prefix=f"{settings.API_V1_STR}/banks", tags=["banks"])
