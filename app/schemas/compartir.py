from pydantic import BaseModel, ConfigDict, Field
    

class CompartirTicket(BaseModel):
    id_usuario_destino: int
    
class InformacionCompartir(BaseModel):
    id_ticket: int | None = None
    id_usuario_origen: int | None = None
    id_usuario_destino: int | None = None
    model_config = ConfigDict(from_attributes=True)