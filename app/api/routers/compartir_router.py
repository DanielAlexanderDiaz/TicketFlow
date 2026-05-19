from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.schemas.compartir import InfoCompartir
from app.services.compartir_services import CompartirServicie


router = APIRouter(prefix="/compartir", tags=["compartir"])

@router.post("/ticket/{id_ticket}", response_model=InfoCompartir, status_code=status.HTTP_201_CREATED)
def compartir_ticket(id_ticket: int, id_usuario_compartido: int, db: DBSession, usuario: UsuarioActual):
    return CompartirServicie(db).compartir_ticket(id_ticket, usuario.id, id_usuario_compartido)
    
# @router.delete("/ticket/{id_ticket}", response_model=InfoCompartir, status_code=status.HTTP_200_OK)
# def quitar_compartir_ticket(id_ticket: int, id_usuario_compartido: int, db: DBSession, usuario: UsuarioActual):
#     CompartirServicie(db).remover_compartir_ticket(id_ticket, usuario.id, id_usuario_compartido)
     
#     return None