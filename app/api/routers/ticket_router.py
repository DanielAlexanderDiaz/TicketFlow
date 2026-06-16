from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from app.api.dependencias import DBSession, UsuarioActual, requiere_admin, puede_gestionar_ticket
from app.models.ticket import EstadoTicket, PrioridadTicket
from app.schemas.ticket import CrearTicket, ActualizarTicket, EliminarTicket, CambioEstadoTicket, AsignarTicket, CompartirTicket, EliminarCompartirTicket, TicketActivo, InformacionTicket, PaginacionTicket
from app.services.ticket_services import TicketService

router = APIRouter(prefix="/ticket", tags=["ticket"])
