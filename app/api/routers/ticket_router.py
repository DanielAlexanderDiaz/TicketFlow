from typing import List

from fastapi import APIRouter, Depends, Query, status
from app.api.dependencias import DBSession, UsuarioActual, ticket_crear, ticket_actualizar, ticket_eliminar, ticket_cambiar_estado, ticket_asignar, ticket_desasignar
from app.schemas.ticket import CrearTicket, ActualizarTicket, EliminarTicket, CambioEstadoTicket, AsignarTicket, InformacionTicket
from app.services.ticket_services import TicketService

router = APIRouter(prefix="/ticket", tags=["ticket"])

@router.post('/crear', response_model=InformacionTicket, status_code=status.HTTP_201_CREATED, dependencies=[Depends(ticket_crear)])
def crear_ticket(db: DBSession, id_usuario: UsuarioActual, payload: CrearTicket):
    servicio = TicketService(db).crear_ticket(id_usuario.id, payload)
    return servicio

@router.patch('/actualizar/{id_ticket}', response_model=InformacionTicket, dependencies=[Depends(ticket_actualizar)])
def actualizar_ticket(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: ActualizarTicket):
    servicio = TicketService(db).actualizar_ticket(id_ticket, id_usuario.id, payload)
    return servicio

@router.delete('/eliminar/{id_ticket}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(ticket_eliminar)])
def eliminar_ticket(db: DBSession, id_usuario: UsuarioActual, payload: EliminarTicket):
    TicketService(db).eliminar_ticket(id_usuario.id, payload)
    return

@router.patch('/estado/{id_ticket}', response_model=InformacionTicket, dependencies=[Depends(ticket_cambiar_estado)])
def cambio_estado_ticket(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: CambioEstadoTicket):
    servicio = TicketService(db).cambio_estado_ticket(id_usuario.id, id_ticket, payload)
    return servicio

@router.patch('/asignar/{id_ticket}', response_model=InformacionTicket, dependencies=[Depends(ticket_asignar)])
def asignar_ticket(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: AsignarTicket):
    servicio = TicketService(db).asignar_ticket(id_ticket, id_usuario.id, payload)
    return servicio

@router.patch('/quitar_asignar/{id_ticket}', response_model=InformacionTicket, dependencies=[Depends(ticket_desasignar)])  
def quitar_asignar_ticket(db: DBSession, id_ticket: int, id_usuario: UsuarioActual):
    servicio = TicketService(db).quitar_asignar_ticket(id_ticket, id_usuario.id)
    return servicio

@router.get("/tickets", response_model=List[InformacionTicket])
def lista_tickets(query: str | None = Query(default=None, description="Texto para buscar por título"), db: DBSession = Depends(), id_usuario: UsuarioActual = Depends()):
    pass