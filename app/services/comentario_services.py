from datetime import datetime
from math import ceil
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.models.auditoria import Auditoria
from app.models.comentario import Comentario
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.schemas.comentario import EliminarComentario, FiltroComentario, InformacionComentario, ActualizarComentario, CrearComentario, PaginacionComentario
from app.repositories.comentario_repository import ComentarioRepositorio


class ComentarioService():
    def __init__(self, db: Session):
        self.comentario_repo = ComentarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.usuario_repo = UsuarioRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def crear_comentario(self, id_ticket: int, id_usuario: int, payload: CrearComentario) -> InformacionComentario:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
        
        # ABAC - Control de acceso
        es_propietario = ticket.id_usuario_creador == id_usuario
        es_asignado = ticket.asignado == id_usuario
        es_compartido = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        es_superadmin = self.usuario_repo.get_usuario_by_id(id_usuario).rol == RolUsuario.SUPERADMIN
        
        if not (es_propietario or es_asignado or es_compartido or es_superadmin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear un comentario en este ticket")
        
        nuevo_comentario = Comentario(id_ticket=id_ticket, id_usuario=id_usuario, comentario=payload.comentario)
        
        comentario = self.comentario_repo.crear_comentario(nuevo_comentario)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "comentario",
            id_entidad = comentario.id,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo=comentario.comentario,
            accion="creado"
        ))
        
        return InformacionComentario.model_validate(comentario)
    
    def actualizar_comentario(self, id_ticket: int, id_comentario: int, id_usuario: int, payload: ActualizarComentario) -> InformacionComentario:
        comentario = self.comentario_repo.get_comentario_by_id(id_comentario)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
        
        es_propietario = comentario.id_usuario == id_usuario
        if not es_propietario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para actualizar este comentario")
        
        ultimo = self.comentario_repo.ultimo_comentario(id_ticket)
        es_ultimo_comentario = comentario.id_ticket == id_ticket and ultimo is not None and comentario.id == ultimo.id
        if not es_ultimo_comentario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se puede modificar un comentario que no sea el último")
        
        comentario_anterior = comentario.comentario
        comentario.comentario = payload.comentario
        comentario.fecha_actualizacion = datetime.now()
        comentario = self.comentario_repo.actualizar_comentario(comentario)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "comentario",
            id_entidad = comentario.id,
            id_usuario = id_usuario,
            campo_cambiado="comentario",
            fecha_cambio=datetime.now(),
            valor_anterior=comentario_anterior,
            valor_nuevo=comentario.comentario,
            accion="actualizado"
        ))
        
        return InformacionComentario.model_validate(comentario)
    
    def eliminar_comentario(self, id_ticket: int, id_usuario: int, payload: EliminarComentario) -> None:
        comentario = self.comentario_repo.get_comentario_by_id(payload.id_comentario)
        if not comentario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
        
        es_propietario = comentario.id_usuario == id_usuario
        if not es_propietario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este comentario")
        
        ultimo = self.comentario_repo.ultimo_comentario(id_ticket)
        es_ultimo_comentario = comentario.id_ticket == id_ticket and ultimo is not None and comentario.id == ultimo.id
        if not es_ultimo_comentario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se puede eliminar un comentario que no sea el último")
        
        self.comentario_repo.eliminar_comentario(comentario.id)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "comentario",
            id_entidad = payload.id_comentario,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="eliminado"
        ))
        
    def listado_comentario(self, id_usuario: int, filtros: FiltroComentario, pagina: int, por_pagina: int)-> InformacionComentario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
        if usuario.rol == RolUsuario.SUPERADMIN:
            ids_permitidos = None
        else:
            ids_propios = set(self.ticket_repo.ids_tickets_propios_o_asignados(id_usuario))
            ids_compartidos = set(self.compartir_repo.tickets_compartidos_con_usuario(id_usuario))
            ids_permitidos = ids_propios | ids_compartidos
            
        offset = (pagina - 1) * por_pagina
        
        total, items = self.comentario_repo.buscar_comentario(
            ids_permitidos=ids_permitidos,
            id_ticket=filtros.id_ticket,
            id_usuario=filtros.id_usuario,
            comentario=filtros.comentario,
            fecha_creacion=filtros.fecha_creacion,
            fecha_actualizacion=filtros.fecha_actualizacion,
            orden=filtros.orden,
            direccion=filtros.direccion,
            limit=por_pagina,
            offset=offset
        )
        
        total_paginas = ceil(total / por_pagina) if total > 0 else 0
        
        return PaginacionComentario(
            total=total,
            total_paginas=total_paginas,
            pagina_actual=pagina,
            tiene_anterior=pagina > 1,
            tiene_siguiente=pagina < total_paginas,
            filtros=filtros,
            items=[InformacionComentario.model_validate(l) for l in items]
        )