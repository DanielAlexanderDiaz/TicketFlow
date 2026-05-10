from fastapi import HTTPException
from sqlmodel import Session
from app.models.usuario import ActualizarUsuario, Usuario
from app.repositories.usuario_repository import UsuarioRepositorio


class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepositorio(db)
        
    def listar_usuario(self, id_usuario: int):
        return self.repo.get_usuario_by_id(id_usuario)
    
    def actualizar_usuario(self, email: int, payload: ActualizarUsuario) -> Usuario:
        usuario = self.repo.get_usuario_by_email(email)
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        
        actualizar = payload.model_dump(exclude_none=True)
        
        for key, value in actualizar.items():
            setattr(usuario, key, value)
        
        self.repo.actualizar_usuario(usuario)
        
        return usuario