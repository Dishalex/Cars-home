from pydantic import BaseModel

class CarCreate(BaseModel):
    plate: str
    model: str

class CarUpdate(BaseModel):
    model: str

class CarResponse(BaseModel):
    id: int
    plate: str
    model: str

class HTTPError(BaseModel):
    detail: str

class SimpleResponse(BaseModel):
    message: str