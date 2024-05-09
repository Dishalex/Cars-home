from typing import Union
from uuid import UUID


from pydantic import BaseModel, Field

class PictureSchema(BaseModel):
    """Pydantic model for validating incoming Picture data."""
    find_plate: str
    url: str
    cloudinary_public_id: str
    history: Union[UUID, int]

