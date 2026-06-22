from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.core.ticket_fsm import TicketFSM
from app.models import ticket
from app.models.auditoria import Auditoria
from app.models.ticket import TRANSICIONES_PERMITIDAS, EstadoTicket, Ticket
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.ticket import ActualizarTicket, AsignarTicket, CambioEstadoTicket, CrearTicket, EliminarTicket, InformacionTicket
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
        
        # ABAC - Control de acceso
        if usuario.rol == RolUsuario.USER:
            es_propietario = id_usuario
        else:
            es_propietario = None
        
        titulo = payload.titulo
        descripcion = payload.descripcion
    
        nuevo_ticket = Ticket(titulo=titulo, descripcion=descripcion, id_usuario_creador=id_usuario, asignado=es_propietario)
        
        ticket = self.ticket_repo.crear_ticket(nuevo_ticket)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = ticket.id,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="creado"
        ))
        
        return InformacionTicket.model_validate(ticket)
    
    def actualizar_ticket(self, id_ticket: int, id_usuario: int, payload: ActualizarTicket) -> InformacionTicket:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no encontrado')
        
        # ABAC - Control de acceso
        es_propietario = ticket.id_usuario_creador == id_usuario
        es_asignado = ticket.asignado == id_usuario
        es_compartido = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        es_superadmin = self.usuario_repo.get_usuario_by_id(id_usuario).rol == RolUsuario.SUPERADMIN
        
        if not (es_propietario or es_asignado or es_compartido or es_superadmin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes permiso para actualizar este ticket')
        
        datos = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not datos:
            return InformacionTicket.model_validate(ticket)
        
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(ticket, campo, None)
            setattr(ticket, campo, nuevo_valor)
            
            if str(valor_anterior) != str(nuevo_valor):
                self.auditoria_repo.crear_audtoria(Auditoria(
                    entidad = "ticket",
                    id_entidad = id_ticket, 
                    id_usuario = id_usuario,
                    campo_cambiado=campo,
                    fecha_cambio=datetime.now(),
                    valor_anterior=str(valor_anterior),
                    valor_nuevo=str(nuevo_valor),
                    accion="actualizado"
                    ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
        return InformacionTicket.model_validate(ticket_actualizado)
    
    def eliminar_ticket(self, id_usuario: int, payload: EliminarTicket) -> None:
        ticket = self.ticket_repo.get_ticket_by_id(payload.id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no encontrado')
        
        # ABAC - Control de acceso
        es_propietario = ticket.id_usuario_creador == id_usuario
        es_superadmin = self.usuario_repo.get_usuario_by_id(id_usuario).rol == RolUsuario.SUPERADMIN
        
        if not (es_propietario or es_superadmin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes permiso para eliminar este ticket')
        
        self.ticket_repo.eliminar_ticket(payload.id_ticket)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = ticket.id,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="Eliminar"
        ))
        
    def cambio_estado_ticket(self, id_usuario: int, id_ticket: int, payload: CambioEstadoTicket) -> InformacionTicket:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no encontrado')
        
        # ABAC - Control de acceso
        es_propietario = ticket.id_usuario_creador == id_usuario
        es_asignado = ticket.asignado == id_usuario
        es_compartido = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        es_superadmin = self.usuario_repo.get_usuario_by_id(id_usuario).rol == RolUsuario.SUPERADMIN
        
        if not (es_propietario or es_asignado or es_compartido or es_superadmin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes permiso para actualizar este ticket')
        
        # FSM - Control de transiciones
        fsm = TicketFSM(ticket.estado)
        try:
            nuevo_estado = fsm.transicionar(payload.estado)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        valor_anterior = ticket.estado
        ticket.estado = nuevo_estado
        ticket.fecha_actualizacion = datetime.now()
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = id_ticket, 
            id_usuario = id_usuario,
            campo_cambiado="estado",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(nuevo_estado),
            accion="actualizado"
        ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
        return InformacionTicket.model_validate(ticket_actualizado)
    
    def asignar_ticket(self, id_ticket: int, id_usuario: int, payload: AsignarTicket) -> InformacionTicket:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no encontrado')
              
        ticket.asignado = payload.id_usuario_asignado
        
        valor_anterior = ticket.asignado
        valor_nuevo = payload.id_usuario_asignado
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = id_ticket, 
            id_usuario = id_usuario,
            campo_cambiado="asignado",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(valor_nuevo),
            accion="actualizado"
        ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
        return InformacionTicket.model_validate(ticket_actualizado)