from math import ceil
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.schemas.auditoria import FiltroAuditoria, InformacionAuditoria, PaginacionAuditoria


class AuditoriaService:
    def __init__(self, db: Session):
        self.auditoria_repo = AuditoriaRepositorio(db)
        self.usuario_repo = UsuarioRepositorio(db)
        
    def listado_auditoria(self, id_usuario: int, filtros: FiltroAuditoria, pagina: int, por_pagina: int) -> PaginacionAuditoria:    
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        if not usuario.rol == RolUsuario.SUPERADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acceso denegado')
        
        offset = (pagina - 1) * por_pagina
        
        total, items = self.auditoria_repo.buscar_auditoria(
            entidad=filtros.entidad,
            id_entidad=filtros.id_entidad,
            id_usuario=filtros.id_usuario,
            campo_cambiado=filtros.campo_cambiado,
            accion=filtros.accion,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            orden=filtros.orden,
            direccion=filtros.direccion,
            limit=por_pagina,
            offset=offset,
        )
        
        total_paginas = ceil(total / por_pagina) if total > 0 else 0
        
        return PaginacionAuditoria(
            total=total,
            total_paginas=total_paginas,
            pagina_actual=pagina,
            tiene_anterior=pagina > 1,
            tiene_siguiente=pagina < total_paginas,
            filtros=filtros,
            items=[InformacionAuditoria.model_validate(l) for l in items]
        )