from datetime import date, time
from enum import Enum
from typing import Annotated, Any
from annotated_types import Ge
from pydantic import BaseModel, BeforeValidator, StringConstraints

def empty_str_to_none(v: Any) -> Any:
    if isinstance(v, str) and not v.strip():
        return None
    return v


def normalize_enum_str(v: Any) -> Any:
    if isinstance(v, str):
        return v.strip().lower().replace(" ", "_")
    return v

Str100 = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
Str255 = Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
Str500 = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
NonNegativeInt = Annotated[int, Ge(0)]

NullableStr100 = Annotated[str | None, BeforeValidator(empty_str_to_none), StringConstraints(strip_whitespace=True, max_length=100)]
NullableStr255 = Annotated[str | None, BeforeValidator(empty_str_to_none), StringConstraints(strip_whitespace=True, max_length=255)]
NullableStr500 = Annotated[str | None, BeforeValidator(empty_str_to_none), StringConstraints(strip_whitespace=True, max_length=500)]

class MealPeriod(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    LATE_NIGHT = "late_night"

class LocationScheduleIngest(BaseModel):
    external_id: Str255
    name: Str255

    start_time: time | None = None
    end_time: time | None = None


class DishIngest(BaseModel):
    external_id: Str255
    name: Str255
    description: NullableStr500 = None
    ingredients: NullableStr500 = None
    calories: NonNegativeInt | None = None
    portion: NullableStr255 = None
    
    period: Annotated[MealPeriod, BeforeValidator(normalize_enum_str)]
    station: Str255 = "General"

class LocationIngest(BaseModel):
    external_id: Str255
    name: Str255
    description: NullableStr500 = None
    location_type: NullableStr100 = None
    
    schedules: list[LocationScheduleIngest] = []
    dishes: list[DishIngest] = []


class DailyMenuIngestPayload(BaseModel):
    served_date: date
    locations: list[LocationIngest]