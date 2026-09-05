import uuid
from typing import Annotated
from annotated_types import Ge, Le
from pydantic import BaseModel, StringConstraints

RatingScore = Annotated[int, Ge(1), Le(10)]
ClientIdStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=255)]


class CreateRatingRequest(BaseModel):
    daily_menu_dishes_id: uuid.UUID
    score: RatingScore


class RatingResponse(BaseModel):
    status: str
    dish_id: uuid.UUID
    user_score: int
    new_average: float
    total_votes: int