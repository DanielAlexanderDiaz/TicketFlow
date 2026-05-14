from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.models.compartir_ticket import solicitudCompartir
from app.services.compartir_services import CompartirServicie


router = APIRouter(prefix="/compartir", tags=["compartir"])

@router.post("/ticket/{id_ticket}", status_code=status.HTTP_201_CREATED)
def compartir_ticket(id_ticket: int, payload: solicitudCompartir, db: DBSession, usuario: UsuarioActual):
    compartir = CompartirServicie(db).compartir_ticket(id_ticket, usuario.id, payload.id_usuario_compartido)
    
    return {
        "id": compartir.id,
        "id_ticket": compartir.id_ticket,
        "id_usuario": compartir.id_usuario
    }
    
@router.delete("/ticket/{id_ticket}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_compartir_ticket(id_ticket: int, id_usuario_compartido: int, db: DBSession, usuario: UsuarioActual):
    CompartirServicie(db).remover_compartir_ticket(id_ticket, usuario.id, id_usuario_compartido)
    return None