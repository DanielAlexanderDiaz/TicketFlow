from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from app.api.dependencias import DBSession, UsuarioActual, ticket_crear, ticket_actualizar
from app.models.ticket import EstadoTicket, PrioridadTicket
from app.schemas.ticket import CrearTicket, ActualizarTicket, EliminarTicket, CambioEstadoTicket, AsignarTicket, CompartirTicket, EliminarCompartirTicket, TicketActivo, InformacionTicket, PaginacionTicket
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