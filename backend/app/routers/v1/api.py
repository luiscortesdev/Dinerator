from fastapi import APIRouter
from app.routers.v1 import admin

api_router = APIRouter()

api_router.include_router(admin.router, prefix="/admin", tags=["admin"])