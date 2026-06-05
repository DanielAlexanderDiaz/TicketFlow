from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CrearComentario(BaseModel):
    comentario: str
    
class ActualizarComentario(BaseModel):
    id_ticket: int
    comentario: str
    
class EliminarComentario(BaseModel):
    id_comentario: int
    
class InformacionComentario(BaseModel):
    id: int
    id_ticket: int
    id_usuario: int
    comentario: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = ConfigDict(from_attributes = True)
    
    