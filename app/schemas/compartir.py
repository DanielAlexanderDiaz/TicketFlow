from pydantic import BaseModel, ConfigDict, Field
    
class InfoCompartir(BaseModel):
    id_ticket: int
    id_usuario_propietario: int
    id_usuario_compartido: int
    model_config = ConfigDict(from_attributes=True)