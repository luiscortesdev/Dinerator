from fastapi import APIRouter
from app.routers.v1 import admin, ratings, location

api_router = APIRouter()

api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(location.router, prefix="/location", tags=["location"])