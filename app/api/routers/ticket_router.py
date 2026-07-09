from datetime import date
from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencias import DBSession, UsuarioActual, ticket_crear, ticket_actualizar, ticket_eliminar, ticket_cambiar_estado, ticket_asignar, ticket_desasignar
from app.models.ticket import EstadoTicket, PrioridadTicket
from app.schemas.ticket import CrearTicket, ActualizarTicket, EliminarTicket, CambioEstadoTicket, AsignarTicket, FiltrosTicket, InformacionTicket, PaginacionTicket
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

@router.delete('/eliminar', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(ticket_eliminar)])
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

@router.get('/tickets', response_model=PaginacionTicket)
def lista_tickets(
    db: DBSession, id_usuario: UsuarioActual,
    buscar_titulo: Optional[str] = Query(default=None, description="Búsqueda parcial por título"),
    buscar_descripcion: Optional[str] = Query(default=None, description="Búsqueda parcial por descripción"),
    id_ticket: Optional[int] = Query(default=None, description="Filtrar por N° de ticket"),
    prioridad: Optional[PrioridadTicket] = Query(default=None, description="Filtrar por prioridad"),
    estado: Optional[EstadoTicket] = Query(default=None, description="Filtrar por estado"),
    asignado: Optional[int] = Query(default=None, description="Filtrar por usuario asignado"),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    orden: Literal["id", "titulo", "prioridad", "estado", "fecha_creacion"] = Query(default="id"),
    direccion: Literal["asc", "desc"] = Query(default="asc"),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=10, ge=1, le=50),
):
    filtros = FiltrosTicket(
        buscar_titulo=buscar_titulo,
        buscar_descripcion=buscar_descripcion,
        id_ticket=id_ticket,
        prioridad=prioridad,
        estado=estado,
        asignado=asignado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        orden=orden,
        direccion=direccion,
    )
    servicio = TicketService(db).listado_ticket(id_usuario.id, filtros, pagina, por_pagina)
    return servicio