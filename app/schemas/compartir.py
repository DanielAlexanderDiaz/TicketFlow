from pydantic import BaseModel, Field


class solicitudCompartir(BaseModel):
    id_usuario_compartido: int = Field(gt=0)     
