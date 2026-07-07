from datetime import date
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencias import DBSession, UsuarioActual, ticket_compartir, ticket_descompartir
from app.schemas.compartir import CompartirTicket, FiltroCompartir, InformacionCompartir, PaginacionCompartir
from app.services.compartir_services import CompartirServicie


router = APIRouter(prefix="/compartir", tags=["compartir"])

@router.post('/compartir/{id_ticket}', response_model=InformacionCompartir, status_code=status.HTTP_201_CREATED, dependencies=[Depends(ticket_compartir)])
def compartir_ticket(db: DBSession, id_usuario: UsuarioActual, id_ticket: int, payload: CompartirTicket) -> InformacionCompartir:
    servicio = CompartirServicie(db).compartir_ticket(id_ticket, id_usuario.id, payload)
    return servicio

@router.delete('/quitar_compartir/{id_ticket}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(ticket_descompartir)])
def quitar_compartir_ticket(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: CompartirTicket) -> None:
    CompartirServicie(db).quitar_compartir_ticket(id_ticket, id_usuario.id, payload)
    
@router.get('/compartidos', response_model=PaginacionCompartir)
def lista_compartidos(
    db: DBSession, id_usuario: UsuarioActual,
    id_ticket: Optional[int] = Query(default=None, description="Filtrar por N° de ticket"),
    id_usuario_origen: Optional[int] = Query(default=None, description="Filtrar por id de usuario origen"),
    id_usuario_destino: Optional[int] = Query(default=None, description="Filtrar por id de usuario destino"),
    fecha_creacion: Optional[date] = Query(default=None),
    orden:  Literal["id", "titulo", "prioridad", "estado", "fecha_creacion"] = Query(default="id"),
    direccion: Literal["asc", "desc"] = Query(default="asc"),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=10, ge=1, le=50),
):
    filtros = FiltroCompartir(
        id_ticket=id_ticket,
        id_usuario_origen=id_usuario_origen,
        id_usuario_destino=id_usuario_destino,
        fecha_creacion=fecha_creacion,
        orden=orden,
        direccion=direccion
    )
    
    servicio = CompartirServicie(db).listado_compartido(id_usuario.id, filtros, pagina, por_pagina)
    return servicio