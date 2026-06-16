from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.auditoria import Auditoria
from app.models.comentario import Comentario
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.schemas.comentario import EliminarComentario, InformacionComentario, ActualizarComentario, CrearComentario
from app.repositories.comentario_repository import ComentarioRepositorio


class ComentarioService():
    def __init__(self, db: Session):
        self.comentario_repo = ComentarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    