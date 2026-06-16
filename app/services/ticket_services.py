from datetime import datetime
from math import ceil
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import ticket
from app.models.auditoria import Auditoria
from app.models.ticket import TRANSICIONES_PERMITIDAS, EstadoTicket, Ticket
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.ticket import ActualizarTicket, AsignarTicket, CambioEstadoTicket, CompartirTicket, CrearTicket, InformacionTicket
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.utils.uploads_file import save_uploaded_img


class TicketService:
    def __init__(self, db: Session):
        self.usuario_repo = UsuarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    