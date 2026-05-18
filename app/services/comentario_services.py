from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.comentario import Comentario
from app.repositories.ticket_repository import TicketRepositorio
from app.schemas.comentario import InfoComentario, ActualizarComentario, CrearComentario
from app.repositories.comentario_repository import ComentarioRepositorio


class ComentarioService():
    def __init__(self, db: Session):
        self.db = db
        self.comentario_repo = ComentarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        
    def comentario_by_id(self, id_comentario: int) -> InfoComentario:
        comentario = self.comentario_repo.get_comentario_by_id(id_comentario)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comentario {id_comentario} no encontrado")
        return InfoComentario.model_validate(comentario)
    
    def comentario_by_ticket(self, id_ticket: int) -> list[InfoComentario]:
        comentario = self.comentario_repo.get_comentario_by_ticket(id_ticket)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {id_ticket} no encontrado")
        return [InfoComentario.model_validate(c) for c in comentario]
    
    def comentario_by_usuario(self, id_usuario: int) -> list[InfoComentario]:
        comentario = self.comentario_repo.get_comentario_by_usuario(id_usuario)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario {id_usuario} no encontrado")
        return [InfoComentario.model_validate(c) for c in comentario]
    
    def crear_comentario(self, id_ticket: int, id_usuario: int, payload: CrearComentario) -> InfoComentario:
        ticket = self.ticket_repo.ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {id_ticket} no encontrado")
        
        comentario = Comentario(**payload.model_dump())
        comentario.id_ticket = id_ticket
        comentario.id_usuario = id_usuario
        comentario.fecha_creacion = datetime.now()
        
        comentario_guardado = self.comentario_repo.crear_comentario(comentario)
        
        return InfoComentario.model_validate(comentario_guardado)
    
    def actualizar_comentario(self, id_comentario: int, id_usuario: int, payload: ActualizarComentario) -> InfoComentario:
        comentario = self.ticket_repo.get_comentario_by_id(id_comentario)
        if comentario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comentario {id_comentario} no encontrado")
        
        es_propietario = comentario.id_usuario == id_usuario 
        if es_propietario is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el comentario {id_comentario}")
        
        datos = payload.model_dump(exclude_unset=True)
        if not datos:
            return InfoComentario.model_validate(comentario)
        
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(comentario, campo, None)
            setattr(comentario, campo, nuevo_valor)
            
        comentario.fecha_actualizacion = datetime.now()    
        comentario_actualizado = self.comentario_repo.actualizar_comentario(comentario)
        
        return InfoComentario.model_validate(comentario_actualizado)
            