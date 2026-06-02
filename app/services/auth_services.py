import datetime
from fastapi import HTTPException, status
from app.core.seguridad import RolUsuario, crear_token, hash_password, verify_password
from app.models.usuario import Usuario
from app.schemas.usuario import Registro, LoginRequest, InformacionUsuario, TokenResponse
from app.repositories.usuario_repository import UsuarioRepositorio


class AuthServices:
    def __init__(self, usuario_repositorio: UsuarioRepositorio):
        self.repo = usuario_repositorio
        
    def registrar(self, payload: Registro) -> InformacionUsuario:
        #validacion
        if self.repo.get_usuario_by_email(payload.email):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        #convertir schema a db
        usuario_db = Usuario(
                        email=payload.email,
                        password=hash_password(payload.password)
                    )
        
        #persistir en db
        usuario_creado = self.repo.crear_usuario(usuario_db)
        return InformacionUsuario.model_validate(usuario_creado)
        

    def login(self, payload: LoginRequest) -> TokenResponse:
        #buscar
        usuario = self.repo.get_usuario_by_email(payload.email)
        
        #validar credenciales
        if not usuario or not verify_password(payload.password, usuario.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas", headers={"WWW-Authenticate": "Bearer"})
        
        if usuario.activo == False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cuenta inactiva", headers={"WWW-Authenticate": "Bearer"})
        
        #generar token
        token_data = {
            "sub": str(usuario.id),
            "rol": usuario.rol,
            "email": usuario.email
        }
        
        access_token = crear_token(token_data)
        
        return TokenResponse(access_token=access_token)