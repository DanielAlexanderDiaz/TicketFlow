from fastapi import HTTPException
from pydantic import EmailStr
from app.core.seguridad import crear_token, hash_password, verify_password
from app.models.usuario import CrearUsuario, Usuario
from app.repositories.usuario_repository import UsuarioRepositorio


class AuthServices:
    def __init__(self, usuario_repositorio: UsuarioRepositorio):
        self.repo = usuario_repositorio
        
    def registrar(self, payload: CrearUsuario) -> Usuario:
        if self.repo.get_usuario_by_email(payload.email):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        usuario = Usuario(
            nombre_usuario = payload.nombre_usuario,
            email = payload.email,
            hashed_password = hash_password(payload.hashed_password[:72])
        )
        return self.repo.crear_usuario(usuario)
    
    def login(self, email: EmailStr, password: str) -> str:
        usuario = self.repo.get_usuario_by_email(email)
        if not usuario or not verify_password(password[:72], usuario.hashed_password):
            raise HTTPException(status_code=400, detail="Credenciales incorrectas")
        
        token = crear_token({"sub": str(usuario.id)})
        return token