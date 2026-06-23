from pydantic import BaseModel, ConfigDict, Field
    

class CompartirTicket(BaseModel):
    id_usuario_compartido: int
    
class InformacionCompartir(BaseModel):
    id_ticket: int | None = None
    id_usuario_propietario: int | None = None
    id_usuario_compartido: int | None = None
    model_config = ConfigDict(from_attributes=True)