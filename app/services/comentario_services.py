from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.auditoria import Auditoria
from app.models.comentario import Comentario
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.schemas.comentario import InformacionComentario, ActualizarComentario, CrearComentario
from app.repositories.comentario_repository import ComentarioRepositorio


class ComentarioService():
    def __init__(self, db: Session):
        self.comentario_repo = ComentarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def comentario_by_id(self, id_comentario: int) -> InformacionComentario:
        comentario = self.comentario_repo.get_comentario_by_id(id_comentario)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comentario {id_comentario} no encontrado")
        return InformacionComentario.model_validate(comentario)
    
    def comentario_by_ticket(self, id_ticket: int) -> list[InformacionComentario]:
        comentario = self.comentario_repo.get_comentario_by_ticket(id_ticket)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {id_ticket} no encontrado")
        return [InformacionComentario.model_validate(c) for c in comentario]
    
    def comentario_by_usuario(self, id_usuario: int) -> list[InformacionComentario]:
        comentario = self.comentario_repo.get_comentario_by_usuario(id_usuario)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario {id_usuario} no encontrado")
        return [InformacionComentario.model_validate(c) for c in comentario]
    
    def crear_comentario(self, id_ticket: int, id_usuario: int, payload: CrearComentario) -> InformacionComentario:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {id_ticket} no encontrado")
        
        es_propietario = self.ticket_repo.es_propietario(id_ticket, id_usuario)
        es_compartido = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        if not es_propietario and not es_compartido:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para crear un comentario en el ticket {id_ticket}")
        
        comentario = Comentario(
            id_ticket=id_ticket,
            id_usuario=id_usuario,
            comentario=payload.comentario
        )
       
        comentario_guardado = self.comentario_repo.crear_comentario(comentario)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "comentario",
            id_entidad=comentario_guardado.id,
            id_usuario=id_usuario,
            id_usuario_compartido=None,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior=None,
            valor_nuevo="comentario creado",
            accion="creado"
        ))
        
        return InformacionComentario.model_validate(comentario_guardado)
    
    def actualizar_comentario(self, id_comentario: int, id_usuario: int, payload: ActualizarComentario) -> InformacionComentario:
        comentario = self.comentario_repo.get_comentario_by_id(id_comentario)
        if comentario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comentario {id_comentario} no encontrado")
        
        es_propietario = comentario.id_usuario == id_usuario 
        if es_propietario is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el comentario {id_comentario}")
        
        datos = payload.model_dump(exclude_unset=True)
        if not datos:
            return InformacionComentario.model_validate(comentario)
        
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(comentario, campo, None)
            setattr(comentario, campo, nuevo_valor)
            
        if str(valor_anterior) != str(nuevo_valor):
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "comentario",
                id_entidad = id_comentario, 
                id_usuario = id_usuario,
                id_usuario_compartido = None,
                campo_cambiado=campo,
                fecha_cambio=datetime.now(),
                valor_anterior=str(valor_anterior),
                valor_nuevo=str(nuevo_valor),
                accion="actualizado"
                ))
            
        comentario.fecha_actualizacion = datetime.now()    
        comentario_actualizado = self.comentario_repo.actualizar_comentario(comentario)
        
        return InformacionComentario.model_validate(comentario_actualizado)
            