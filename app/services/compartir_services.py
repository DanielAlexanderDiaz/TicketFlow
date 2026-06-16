from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.auditoria import Auditoria
from app.models.compartir_ticket import TicketCompartir
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.schemas.compartir import InformacionCompartir
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio


class CompartirServicie:
    def __init__(self, db: Session):
        self.db = db
        self.compartir_repo = CompartirRepository(db)
        self.ticket_repo = TicketRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        self.usuario_repo = UsuarioRepositorio(db)
                
    