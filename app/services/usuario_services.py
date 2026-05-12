from fastapi import HTTPException, Query
from sqlmodel import Session
from app.models.usuario import ActualizarUsuario, Usuario
from app.repositories.usuario_repository import UsuarioRepositorio


class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepositorio(db)
        
    def listar_usuarios(self) -> list[Usuario]:
        lista = self.repo.listar_usuarios()
        if not lista:
            raise HTTPException(status_code=404, detail='No se encontraron usuarios')
        return lista
        
    def informacion_usuario(self, id_usuario: int):
        usuario = self.repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        return usuario
    
    def informacio_usuario_id(self, id_usuario: int):
        usuario = self.repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        return usuario
    
    def actualizar_usuario_id(self, id_usuario: int, payload: ActualizarUsuario) -> Usuario:
        usuario = self.repo.get_usuario_by_id(id_usuario)
        
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        
        actualizar = payload.model_dump(exclude_unset=True)
        
        for key, value in actualizar.items():
            setattr(usuario, key, value)
            
        self.repo.actualizar_usuario(usuario)
        
        return usuario
    
    def actualizar_usuario_id(self,id_usuario: int, payload: ActualizarUsuario) -> Usuario:
        usuario = self.repo.get_usuario_by_id(id_usuario)
        
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        
        actualizar = payload.model_dump(exclude_unset=True)
        
        for key, value in actualizar.items():
            setattr(usuario, key, value)
            
        self.repo.actualizar_usuario(usuario)
        
        return usuario