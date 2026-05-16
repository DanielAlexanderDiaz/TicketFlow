from fastapi import HTTPException, Query, status
from sqlmodel import Session
from app.models.usuario import Usuario
from app.schemas.usuario import ActualizarRol, ActualizarUsuario, InfoUsuario
from app.repositories.usuario_repository import UsuarioRepositorio

class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.usuario_repo = UsuarioRepositorio(db)
        
    def listar_usuarios(self) -> list[InfoUsuario]:
        lista = self.usuario_repo.listar_usuarios()
        if not lista:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No se encontraron usuarios')
        return InfoUsuario.model_validate(lista)
        
    def informacion_usuario(self, id_usuario: int):
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        return InfoUsuario.model_validate(usuario)
    
    def informacio_usuario_id(self, id_usuario: int):
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        return InfoUsuario.model_validate(usuario)
    
    def actualizar_usuario_id(self, id_usuario: int, payload: ActualizarUsuario) -> InfoUsuario:
        # valida
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        datos = payload.model_dump(exclude_unset=True)
        if not datos:
            return InfoUsuario.model_validate(usuario)
        
        # obtener valores anteriores
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(usuario, campo, None)
            setattr(usuario, campo, nuevo_valor)
            
        usuario_actualizado = self.usuario_repo.actualizar_usuario(usuario)
        
        return InfoUsuario.model_validate(usuario_actualizado)
    
    def actualizar_rol(self, id_usuario: int, payload: ActualizarRol) -> InfoUsuario:
        # valida
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)    
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')

        usuario.rol = payload.rol
        usuario_actualizado = self.usuario_repo.actualizar_usuario(usuario)
        
        return InfoUsuario.model_validate(usuario_actualizado)