from pydantic import BaseModel, ConfigDict


class CrearAuditoria(BaseModel):
    entidad: str
    id_entidad: int
    id_usuario: int
    campo_cambiado: str
    fecha_cambio: str
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    accion: str

class InformacionAuditoria(BaseModel):
    entidad: str
    id_entidad: int
    id_usuario: int
    id_usuario_compartido: int | None = None
    campo_cambiado: str
    fecha_cambio: str
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    accion: str
    model_config = ConfigDict(from_attributes = True)