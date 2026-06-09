from datetime import datetime
from fastapi import HTTPException, Query, status
from sqlmodel import Session
from app.models.auditoria import Auditoria
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.usuario import ActualizarPermisos, ActualizarRol, ActualizarUsuario, EliminarUsuario, InformacionUsuario, UsuarioActivo
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
        
        self.usuario_repo.actualizar_usuario(usuario)
        
        return InformacionUsuario.model_validate(usuario)
        
    def eliminar_usuario(self, payload: EliminarUsuario) -> bool:
        usuario = self.usuario_repo.get_usuario_by_id(payload.id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "usuario",
            id_entidad = payload.id,
            id_usuario = payload.id,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="*",
            accion="eliminado"
        ))
        
        return self.usuario_repo.eliminar_usuario(usuario)
    
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
        
        usuario.permisos = payload.permisos
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "usuario",
            id_entidad = id_usuario, 
            id_usuario = id_usuario,
            campo_cambiado="permisos",
            fecha_cambio=datetime.now(),
            valor_anterior=str(usuario.permisos),
            valor_nuevo=str(payload.permisos),
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
    
    
    
    
    
    
    