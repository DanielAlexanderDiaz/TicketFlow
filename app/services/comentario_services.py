from sqlmodel import Session
from app.models.comentario import ComentarioTicket, CrearComentarioTicket
from app.repositories.comentario_repository import ComentarioRepositorio


class ComentarioService():
    def __init__(self, db: Session):
        self.repo = ComentarioRepositorio(db)
        
    def comentario_by_id(self, id_comentario: int) -> list[ComentarioTicket]:
        return self.repo.get_comentario_by_id(id_comentario)
    
    def comentario_by_ticket(self, id_ticket: int) -> list[ComentarioTicket]:
        return self.repo.get_comentario_by_ticket(id_ticket)
    
    def crear_comentario(self, comentario: CrearComentarioTicket) -> ComentarioTicket:
        return self.repo.crear_comentario(comentario)
    