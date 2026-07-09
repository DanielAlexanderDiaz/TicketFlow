from datetime import datetime
from math import ceil
from fastapi import HTTPException, Query, status
from sqlmodel import Session
from app.core.seguridad import RolUsuario
from app.models.auditoria import Auditoria
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.usuario import ActualizarPermisos, ActualizarRol, ActualizarUsuario, FiltrosUsuario, InformacionUsuario, PaginacionUsuario, UsuarioActivo
from app.repositories.usuario_repository import UsuarioRepositorio
from app.utils.uploads_file import save_uploaded_img

class UsuarioService:
    def __init__(self, db: Session):
        self.usuario_repo = UsuarioRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def actualizar_usuario(self, id_usuario: int, payload: ActualizarUsuario) -> InformacionUsuario:
        # valida
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
           
        datos = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not datos:
            return InformacionUsuario.model_validate(usuario)
        
        # obtener valores anteriores
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(usuario, campo, None)
            setattr(usuario, campo, nuevo_valor)
            
            if str(valor_anterior) != str(nuevo_valor):
                self.auditoria_repo.crear_audtoria(Auditoria(
                    entidad = "usuario",
                    id_entidad = id_usuario, 
                    id_usuario = id_usuario,
                    campo_cambiado=campo,
                    fecha_cambio=datetime.now(),
                    valor_anterior=str(valor_anterior),
                    valor_nuevo=str(nuevo_valor),
                    accion="actualizado"
                    ))
            
        usuario_actualizado = self.usuario_repo.actualizar_usuario(usuario)
        
        return InformacionUsuario.model_validate(usuario_actualizado)
    
    def actualizar_imagen(self, id_usuario: int, imagen_url: str) -> InformacionUsuario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        img_data = save_uploaded_img(imagen_url)
        usuario.imagen_url = img_data["url"]
        
        valor_anterior = usuario.imagen_url
        valor_nuevo = img_data["url"]
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "usuario",
            id_entidad = id_usuario, 
            id_usuario = id_usuario,
            campo_cambiado="imagen_url",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(valor_nuevo),
            accion="actualizado"
            ))
        
        self.usuario_repo.actualizar_usuario(usuario)
        
        return InformacionUsuario.model_validate(usuario)
        
    def eliminar_usuario(self, id_usuario: int) -> None:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "usuario",
            id_entidad = id_usuario,
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="eliminado"
        ))
        
        self.usuario_repo.eliminar_usuario(usuario)
    
    def actualizar_rol(self, id_usuario: int, payload: ActualizarRol) -> InformacionUsuario:
        # valida
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)    
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
       
        datos = payload.model_dump(exclude_unset=True)
        if not datos:
            return InformacionUsuario.model_validate(usuario)
        
        # obtener valores anteriores
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(usuario, campo, None)
            setattr(usuario, campo, nuevo_valor)
            
            if str(valor_anterior) != str(nuevo_valor):
                self.auditoria_repo.crear_audtoria(Auditoria(
                    entidad = "usuario",
                    id_entidad = id_usuario, 
                    id_usuario = id_usuario,
                    campo_cambiado=campo,
                    fecha_cambio=datetime.now(),
                    valor_anterior=str(valor_anterior),
                    valor_nuevo=str(nuevo_valor),
                    accion="actualizado"
                    ))

        usuario_actualizado = self.usuario_repo.actualizar_usuario(usuario)
        
        return InformacionUsuario.model_validate(usuario_actualizado)
    
    def actualizar_permisos(self, id_usuario: int, payload: ActualizarPermisos) -> InformacionUsuario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        valor_anterior = list(usuario.permiso)
        
        usuario.permiso = payload.permiso
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "usuario",
            id_entidad = id_usuario, 
            id_usuario = id_usuario,
            campo_cambiado="permisos",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(payload.permiso),
            accion="actualizado"
            ))
        
        self.usuario_repo.actualizar_usuario(usuario)
        
        return InformacionUsuario.model_validate(usuario)
    
    def usuario_activo(self, id_usuario: int, payload: UsuarioActivo) -> InformacionUsuario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        valor_anterior = usuario.activo
        nuevo_valor = payload.activo
        
        usuario.activo = payload.activo
        
        if str(valor_anterior) != str(nuevo_valor):
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "usuario",
                id_entidad = id_usuario, 
                id_usuario = id_usuario,
                campo_cambiado="activo",
                fecha_cambio=datetime.now(),
                valor_anterior=str(valor_anterior),
                valor_nuevo=str(nuevo_valor),
                accion="actualizado"
                ))
        
        self.usuario_repo.actualizar_usuario(usuario)
        
        return InformacionUsuario.model_validate(usuario)
    
    def listar_usuarios(self) -> list[InformacionUsuario]:
        lista = self.usuario_repo.listar_usuarios()
        if not lista:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No se encontraron usuarios')
        return [InformacionUsuario.model_validate(l) for l in lista]
        
    def informacion_usuario(self, id_usuario: int):
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        return InformacionUsuario.model_validate(usuario)
    
    def informacio_usuario_id(self, id_usuario: int):
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        return InformacionUsuario.model_validate(usuario)
    
    def listado_usuario(self, id_usuario: int, filtros: FiltrosUsuario, pagina: int, por_pagina: int) -> PaginacionUsuario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        if not usuario.rol == RolUsuario.SUPERADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acceso denegado')
        
        offset = (pagina - 1) * por_pagina
        
        total, items = self.usuario_repo.buscar_usuario(
            buscar_email=filtros.buscar_email,
            buscar_nombre=filtros.buscar_nombre,
            rol=filtros.rol,
            activo=filtros.activo,
            orden=filtros.orden,
            direccion=filtros.direccion,
            limit=por_pagina,
            offset=offset,
        )
        
        total_paginas = ceil(total / por_pagina) if total > 0 else 0
        
        return PaginacionUsuario(
            total=total,
            total_paginas=total_paginas,
            pagina_actual=pagina,
            tiene_anterior=pagina > 1,
            tiene_siguiente=pagina < total_paginas,
            filtros=filtros,
            items=[InformacionUsuario.model_validate(l) for l in items] 
        )
            
        
    
    
    
    
    