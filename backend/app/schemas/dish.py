from pydantic import BaseModel
from datetime import date
import uuid

from app.models.enums import MealPeriod

class DailyMenuDishRead(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    dish_id: uuid.UUID
    served_date: date
    period: MealPeriod
    station: str