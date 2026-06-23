from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.models.auditoria import Auditoria
from app.models.compartir_ticket import TicketCompartir
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.schemas.compartir import CompartirTicket, InformacionCompartir



class CompartirServicie:
    def __init__(self, db: Session):
        self.db = db
        self.compartir_repo = CompartirRepository(db)
        self.ticket_repo = TicketRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        self.usuario_repo = UsuarioRepositorio(db)
                
    def compartir_ticket(self, id_ticket: int, id_usuario: int, payload: CompartirTicket) -> InformacionCompartir:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no encontrado')
        
        # ABAC - Control de acceso
        es_propietario = ticket.id_usuario_creador == id_usuario
        es_asignado = ticket.asignado == id_usuario
        es_superadmin = self.usuario_repo.get_usuario_by_id(id_usuario).rol == RolUsuario.SUPERADMIN
        
        if not (es_propietario or es_asignado or es_superadmin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes permiso para compartir este ticket')
        
        nuevo_compartir = TicketCompartir(id_ticket=id_ticket, id_usuario_origen=id_usuario, id_usuario_destino=payload.id_usuario_destino)
        
        compartir = self.compartir_repo.compartir_ticket(nuevo_compartir)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "compartir_ticket",
            id_entidad = compartir.id,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="creado"
        ))
        
        return InformacionCompartir.model_validate(compartir)
    
    def quitar_compartir_ticket(self, id_ticket: int, id_usuario: int, payload: CompartirTicket) -> None:
        ticket_compartido = self.compartir_repo.ticket_compartido(id_ticket)
        
        if not ticket_compartido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no compartido')
        
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        
        # ABAC - Control de acceso
        es_propietario = ticket.id_usuario_creador == id_usuario
        es_asignado = ticket.asignado == id_usuario
        es_superadmin = self.usuario_repo.get_usuario_by_id(id_usuario).rol == RolUsuario.SUPERADMIN
        
        if not (es_propietario or es_asignado or es_superadmin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes permiso para quitar compartir este ticket')
        
        quitar_compartir = payload.id_usuario_destino
        
        self.compartir_repo.eliminar_compartir_ticket(id_ticket, quitar_compartir)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "compartir_ticket",
            id_entidad = ticket.id,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="eliminado"
        ))