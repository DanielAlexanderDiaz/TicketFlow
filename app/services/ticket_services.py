from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import ticket
from app.models.auditoria import Auditoria
from app.models.ticket import TRANSICIONES_PERMITIDAS, EstadoTicket, Ticket
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.ticket import CrearTicket, InformacionTicket
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
        
    def crear_ticket(self, id_usuario: int, payload: CrearTicket) -> InformacionTicket:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        titulo = payload.titulo
        descripcion = payload.descripcion
        
        nuevo_ticket = Ticket(titulo=titulo, descripcion=descripcion, id_usuario_creador=id_usuario)
        
        ticket = self.ticket_repo.crear_ticket(nuevo_ticket)
        
        return InformacionTicket.model_validate(ticket)