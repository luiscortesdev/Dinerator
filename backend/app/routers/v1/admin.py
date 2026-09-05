import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.deps import get_db
from app.models.dining import DailyMenuDish, Dish, Location, LocationSchedule
from app.schemas.ingest import DailyMenuIngestPayload

router = APIRouter()

API_KEY_HEADER = APIKeyHeader(name="X-Admin-Key", auto_error=True)

load_dotenv()

ADMIN_INGEST_KEY = os.getenv("ADMIN_INGEST_KEY", "dev-secret-key")

async def verify_admin_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if api_key != ADMIN_INGEST_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing ingestion API key",
        )
    return api_key


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_daily_menu(
    payload: DailyMenuIngestPayload,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin_key),
):
    try:
        total_dishes_synced = 0

        for loc_data in payload.locations:
            loc_stmt = (
                pg_insert(Location)
                .values(
                    external_id=loc_data.external_id,
                    name=loc_data.name,
                    description=loc_data.description,
                    location_type=loc_data.location_type,
                )
                .on_conflict_do_update(
                    index_elements=[Location.external_id],
                    set_={
                        "name": loc_data.name,
                        "description": loc_data.description,
                        "location_type": loc_data.location_type,
                    },
                )
                .returning(Location.id)
            )
            loc_result = await db.execute(loc_stmt)
            location_id = loc_result.scalar_one()
            
            for sched in loc_data.schedules:
                sched_stmt = (
                    pg_insert(LocationSchedule)
                    .values(
                        location_id=location_id,
                        external_id=sched.external_id,
                        name=sched.name,
                        start_time=sched.start_time,
                        end_time=sched.end_time,
                    )
                    .on_conflict_do_update(
                        index_elements=[LocationSchedule.external_id],
                        set_={
                            "name": sched.name,
                            "start_time": sched.start_time,
                            "end_time": sched.end_time,
                        },
                    )
                )
                await db.execute(sched_stmt)

            for dish in loc_data.dishes:
                # Upsert master dish catalog
                dish_stmt = (
                    pg_insert(Dish)
                    .values(
                        location_id=location_id,
                        external_id=dish.external_id,
                        name=dish.name,
                        description=dish.description,
                        ingredients=dish.ingredients,
                        calories=dish.calories,
                        portion=dish.portion,
                    )
                    .on_conflict_do_update(
                        constraint="dishes_name_location_unique",
                        set_={
                            "external_id": dish.external_id,
                            "description": dish.description,
                            "ingredients": dish.ingredients,
                            "calories": dish.calories,
                            "portion": dish.portion,
                        },
                    )
                    .returning(Dish.id)
                )
                dish_result = await db.execute(dish_stmt)
                dish_id = dish_result.scalar_one()

                # Record daily serving occurrence
                serving_stmt = (
                    pg_insert(DailyMenuDish)
                    .values(
                        location_id=location_id,
                        dish_id=dish_id,
                        served_date=payload.served_date,
                        period=dish.period,
                        station=dish.station,
                    )
                    .on_conflict_do_nothing(
                        constraint="unique_daily_serving"
                    )
                )
                await db.execute(serving_stmt)
                total_dishes_synced += 1

        # Commit everything atomically
        await db.commit()

        return {
            "status": "success",
            "served_date": payload.served_date.isoformat(),
            "locations_processed": len(payload.locations),
            "dishes_synced": total_dishes_synced,
        }

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest menu: {str(exc)}",
        ) from exc