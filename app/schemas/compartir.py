from pydantic import BaseModel, ConfigDict, Field


class SolicitudCompartir(BaseModel):
    id_usuario_compartido: int = Field(gt=0)     
    
class InfoCompartir(BaseModel):
    id_usuario: int
    id_usuario_compartido: int
    model_config = ConfigDict(from_attributes=True)