import uuid
from pydantic import BaseModel

class LocationRead(BaseModel):
    id: uuid.UUID
    external_id: str
    name: str
    description: str | None = None
    location_type: str | None = None