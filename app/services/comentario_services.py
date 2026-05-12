from fastapi import HTTPException
from sqlmodel import Session
from app.models.comentario import Comentario, ActualizarComentario, CrearComentario, InfoComentario
from app.repositories.comentario_repository import ComentarioRepositorio
from app.services.ticket_services import TicketService


class ComentarioService():
    def __init__(self, db: Session):
        self.repo = ComentarioRepositorio(db)
        self.ticket = TicketService(db)
        
    def comentario_by_id(self, id_comentario: int) -> Comentario:
        comentario = self.repo.get_comentario_by_id(id_comentario)
        if not comentario:
            raise HTTPException(status_code=404, detail=f"Comentario {id_comentario} no encontrado")
        return comentario
    
    def comentario_by_ticket(self, id_ticket: int) -> list[Comentario]:
        comentario = self.repo.get_comentario_by_ticket(id_ticket)
        if not comentario:
            raise HTTPException(status_code=404, detail=f"Ticket {id_ticket} no encontrado")
        return comentario
    
    def comentario_by_usuario(self, id_usuario: int) -> list[Comentario]:
        comentario = self.repo.get_comentario_by_usuario(id_usuario)
        if not comentario:
            raise HTTPException(status_code=404, detail=f"Usuario {id_usuario} no encontrado")
        return comentario
    
    def crear_comentario(self, id_ticket: int, id_usuario: int, payload: CrearComentario) -> Comentario:
        ticket = self.ticket.ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {id_ticket} no encontrado")
        
        comentario = Comentario(**payload.model_dump())
        comentario.id_ticket = id_ticket
        comentario.id_usuario = id_usuario
        
        return self.repo.crear_comentario(comentario)
    
    def actualizar_comentario(self, id_comentario: int, id_ticket: int, payload: ActualizarComentario) -> Comentario:
        comentario = self.repo.get_comentario_by_id(id_comentario)
        ticket = self.repo.get_comentario_by_ticket(id_ticket)
        if comentario is None or ticket is None:
            raise HTTPException(status_code=404, detail=f"Comentario {id_comentario} no encontrado o ticket {id_ticket} no encontrado")
        
        actualizar = payload.model_dump(exclude_unset=True)
        
        for key, value in actualizar.items():
            setattr(comentario, key, value)
            
        return self.repo.actualizar_comentario(comentario)