from datetime import datetime
from math import ceil
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.models.auditoria import Auditoria
from app.models.compartir_ticket import TicketCompartir
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.schemas.compartir import CompartirTicket, FiltroCompartir, InformacionCompartir, PaginacionCompartir



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
        
    def listado_compartido(self, _id_usuario: int, filtros: FiltroCompartir, pagina: int, por_pagina: int) -> InformacionCompartir:
        usuario = self.usuario_repo.get_usuario_by_id(_id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
        if usuario.rol == RolUsuario.SUPERADMIN:
            ids_permitidos = None
        else:
            ids_propios = set(self.compartir_repo.ids_tickets_compartidos_por_usuario_origen(_id_usuario))
            ids_permitidos = ids_propios
            
        offset = (pagina - 1) * por_pagina
        
        total, items = self.compartir_repo.buscar_compartidos(
            ids_permitidos=ids_permitidos,
            id_ticket=filtros.id_ticket,
            id_usuario_origen=filtros.id_usuario_origen,
            id_usuario_destino=filtros.id_usuario_destino,
            fecha_creacion=filtros.fecha_creacion,
            orden=filtros.orden,
            direccion=filtros.direccion,
            limit=por_pagina,
            offset=offset
        )
        
        total_paginas = ceil(total / por_pagina) if total > 0 else 0
        
        return PaginacionCompartir(
            total=total,
            total_paginas=total_paginas,
            pagina_actual=pagina,
            tiene_anterior=pagina > 1,
            tiene_siguiente=pagina < total_paginas,
            filtros=filtros,
            items=[InformacionCompartir.model_validate(compartir) for compartir in items]
        )