from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.deps import get_db
from app.models.dining import DailyMenuDish, Rating
from app.schemas.ratings import CreateRatingRequest, RatingResponse

router = APIRouter()

# submit or update rating post endpoint
@router.post("", response_model=RatingResponse, status_code=status.HTTP_200_OK)
async def submit_dish_rating(
    payload: CreateRatingRequest,
    x_client_id: Annotated[str | None, Header(description="Anonymous client UUID from localStorage")] = None,
    db: AsyncSession = Depends(get_db),
):
    if not x_client_id or len(x_client_id.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing or invalid client identifier header (X-Client-Id)",
        )

    dish_exists = await db.scalar(
        select(DailyMenuDish.id).where(DailyMenuDish.id == payload.daily_menu_dishes_id)
    )
    if not dish_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily menu dish not found",
        )

    rating_statement = (
        pg_insert(Rating)
        .values(
            daily_menu_dishes_id=payload.daily_menu_dishes_id,
            score=payload.score,
            client_id=x_client_id,
        )
        .on_conflict_do_update(
            constraint="unique_user_daily_rating",
            set_={
                "score": payload.score,
                "created_at": func.now(),
            },
        )
    )
    await db.execute(rating_statement)
    await db.commit()

    # calculate updated ratings stats to return to frontend
    stats_query = select(
        func.coalesce(func.round(func.avg(Rating.score), 1), 0.0).label("average"),
        func.count(Rating.id).label("total"),
    ).where(Rating.daily_menu_dishes_id == payload.daily_menu_dishes_id)

    stats_res = (await db.execute(stats_query)).one()
    new_avg, total_votes = stats_res

    return RatingResponse(
        status="success",
        dish_id=payload.daily_menu_dishes_id,
        user_score=payload.score,
        new_average=float(new_avg),
        total_votes=int(total_votes),
    )