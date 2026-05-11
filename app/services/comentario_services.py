from fastapi import HTTPException
from sqlmodel import Session
from app.models.comentario import Comentario, ActualizarComentario, CrearComentario, InfoComentario
from app.repositories.comentario_repository import ComentarioRepositorio


class ComentarioService():
    def __init__(self, db: Session):
        self.repo = ComentarioRepositorio(db)
        
    def comentario_by_id(self, id_comentario: int) -> list[Comentario]:
        return self.repo.get_comentario_by_id(id_comentario)
    
    def comentario_by_ticket(self, id_ticket: int) -> list[Comentario]:
        return self.repo.get_comentario_by_ticket(id_ticket)
    
    def crear_comentario(self, comentario: CrearComentario) -> Comentario:
        return self.repo.crear_comentario(comentario)
    
    def actualizar_comentario(self, id_comentario: int, payload: ActualizarComentario) -> Comentario:
        comentario = self.repo.get_comentario_by_id(id_comentario)
        if comentario is None:
            raise HTTPException(status_code=404, detail=f"Comentario {id_comentario} no encontrado")
        
        actualizar = payload.model_dump(exclude_unset=True)
        
        for key, value in actualizar.items():
            setattr(comentario, key, value)
            
        return self.repo.actualizar_comentario(comentario)