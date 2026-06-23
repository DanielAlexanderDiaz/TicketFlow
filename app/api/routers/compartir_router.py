from fastapi import APIRouter, Depends, status
from app.api.dependencias import DBSession, UsuarioActual, ticket_compartir, ticket_descompartir
from app.schemas.compartir import CompartirTicket, InformacionCompartir
from app.services.compartir_services import CompartirServicie


router = APIRouter(prefix="/compartir", tags=["compartir"])

@router.post('/compartir', response_model=InformacionCompartir, status_code=status.HTTP_201_CREATED, dependencies=[Depends(ticket_compartir)])
def compartir_ticket(db: DBSession, id_usuario: UsuarioActual, id_ticket: int, payload: CompartirTicket) -> InformacionCompartir:
    servicio = CompartirServicie(db).compartir_ticket(id_ticket, id_usuario.id, payload)
    return servicio

@router.delete('/quitar_compartir/{id_ticket}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(ticket_descompartir)])
def quitar_compartir_ticket(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: CompartirTicket) -> None:
    CompartirServicie(db).quitar_compartir_ticket(id_ticket, id_usuario.id, payload)