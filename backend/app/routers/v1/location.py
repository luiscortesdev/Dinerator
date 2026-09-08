from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.deps import get_db
from app.models.dining import Location
from app.schemas.location import LocationRead

router = APIRouter()

@router.get("", response_model=list[LocationRead], status_code=status.HTTP_200_OK)
async def get_all_locations(
    x_client_id: Annotated[str | None, Header(description="Anonymous client UUID from localStorage")] = None,
    db: AsyncSession = Depends(get_db)
):
    if not x_client_id or len(x_client_id.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing or invalid client identifier header (X-Client-Id)"
        )

    query = select(Location)
    locations = (await db.scalars(query)).all()
    
    return locations