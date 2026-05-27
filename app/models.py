from pydantic import BaseModel, Field


class DonacionRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    producto_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)


class DonacionResponse(BaseModel):
    ok: bool = True
    mensaje: str


class ErrorResponse(BaseModel):
    error: str
