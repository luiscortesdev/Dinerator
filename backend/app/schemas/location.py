import uuid
from pydantic import BaseModel, Field

from app.schemas.dish import DailyMenuDishRead

class LocationRead(BaseModel):
    id: uuid.UUID
    external_id: str
    name: str
    description: str | None = None
    location_type: str | None = None
    
class LocationReadWithMenu(LocationRead):
    menu: list[DailyMenuDishRead] = Field(default=[], validation_alias="daily_menu_dishes")