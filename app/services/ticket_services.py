from datetime import datetime
from math import ceil
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.core.ticket_fsm import TicketFSM
from app.models.auditoria import Auditoria
from app.models.ticket import Ticket
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.comentario_repository import ComentarioRepositorio
from app.schemas.ticket import ActualizarTicket, AsignarTicket, CambioEstadoTicket, CrearTicket, EliminarTicket, FiltrosTicket, InformacionTicket, PaginacionTicket
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.utils.uploads_file import save_uploaded_img


class TicketService:
    def __init__(self, db: Session):
        self.usuario_repo = UsuarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.comentario_repo = ComentarioRepositorio(db)
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
        
        comentarios = self.comentario_repo.get_comentario_by_ticket(payload.id_ticket)
        for comentario in comentarios:
            self.comentario_repo.eliminar_comentario(comentario.id)
            
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "comentario",
                id_entidad = comentario.id,
                id_usuario = id_usuario,
                campo_cambiado="*",
                fecha_cambio=datetime.now(),
                valor_anterior="*",
                valor_nuevo="*",
                accion="eliminado"
            ))
            
        compartidos = self.compartir_repo.todos_compartidos_ticket(payload.id_ticket)
        for compartir in compartidos:
            self.compartir_repo.eliminar_todos_compartidos(payload.id_ticket)
            
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "compartir_ticket",
                id_entidad = compartir.id,
                id_usuario = id_usuario,
                campo_cambiado="*",
                fecha_cambio=datetime.now(),
                valor_anterior="*",
                valor_nuevo="*",
                accion="eliminado"
            ))
        
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
              
        valor_anterior = ticket.asignado
        valor_nuevo = payload.id_usuario_asignado
        
        ticket.asignado = payload.id_usuario_asignado
          
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
    
    def quitar_asignar_ticket(self, id_ticket: int, id_usuario: int) -> InformacionTicket:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket no encontrado')
        
        if ticket.asignado is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='El ticket no está asignado')
        
        valor_anterior = ticket.asignado
        ticket.asignado = None
          
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = id_ticket, 
            id_usuario = id_usuario,
            campo_cambiado="asignado",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo="None",
            accion="actualizado"
        ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
        return InformacionTicket.model_validate(ticket_actualizado)
    
    def listado_ticket(self, id_usuario: int, filtros: FiltrosTicket, pagina: int, por_pagina: int) -> PaginacionTicket:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')

        # RF-21 - ABAC: superadmin ve todo, el resto ve solo lo suyo (unión de sets)
        if usuario.rol == RolUsuario.SUPERADMIN:
            ids_permitidos = None
        else:
            ids_propios = set(self.ticket_repo.ids_tickets_propios_o_asignados(id_usuario))
            ids_compartidos = set(self.compartir_repo.tickets_compartidos_con_usuario(id_usuario))
            ids_permitidos = ids_propios | ids_compartidos

        offset = (pagina - 1) * por_pagina

        total, items = self.ticket_repo.buscar_ticket(
            ids_permitidos=ids_permitidos,
            buscar_titulo=filtros.buscar_titulo,
            buscar_descripcion=filtros.buscar_descripcion,
            id_ticket=filtros.id_ticket,
            prioridad=filtros.prioridad,
            estado=filtros.estado,
            asignado=filtros.asignado,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            orden=filtros.orden,
            direccion=filtros.direccion,
            limit=por_pagina,
            offset=offset,
        )

        total_paginas = ceil(total / por_pagina) if total > 0 else 0

        return PaginacionTicket(
            total=total,
            total_paginas=total_paginas,
            pagina_actual=pagina,
            tiene_anterior=pagina > 1,
            tiene_siguiente=pagina < total_paginas,
            filtros=filtros,
            items=[InformacionTicket.model_validate(t) for t in items]
        )