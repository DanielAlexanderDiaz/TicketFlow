from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencias import DBSession, UsuarioActual, ticket_crear, ticket_actualizar, ticket_eliminar, ticket_cambiar_estado, ticket_asignar, ticket_desasignar
from app.schemas.ticket import CrearTicket, ActualizarTicket, EliminarTicket, CambioEstadoTicket, AsignarTicket, InformacionTicket, PaginacionTicket
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

@router.get("/tickets", response_model=PaginacionTicket)
def lista_tickets(db: DBSession, id_usuario: UsuarioActual, query: Optional[str] | None = Query(default=None, description="Texto para buscar por título"), 
                por_pagina: int = Query(default=10, ge=1, le=50, description="Cantidad de tickets por pagina"),
                pagina: int = Query(default=1, ge=1, description="Pagina de tickets"),
                orden: Literal["id", "titulo"] = Query(default="id", description="Ordenar por id o titulo"),
                direccion: Literal["asc", "desc"] = Query(default="asc", description="Orden ascendente o descendente")
                ):
    servicio = TicketService(db).listado_ticket(query, orden, direccion, pagina, por_pagina)
    return servicio