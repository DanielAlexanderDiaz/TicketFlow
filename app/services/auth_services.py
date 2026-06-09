from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.seguridad import crear_token, hash_password, verify_password
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.usuario import Registro, LoginRequest, InformacionUsuario, TokenResponse
from app.repositories.usuario_repository import UsuarioRepositorio


class AuthServices:
    def __init__(self, db: Session):        
        self.usuario_repo = UsuarioRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def registrar(self, payload: Registro) -> InformacionUsuario:
        #validacion
        if self.usuario_repo.get_usuario_by_email(payload.email):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        #convertir schema a db
        usuario_db = Usuario(
                        email=payload.email,
                        password=hash_password(payload.password)
                    )
        
        #persistir en db
        usuario_creado = self.usuario_repo.crear_usuario(usuario_db)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad="Usuario",
            id_entidad=usuario_creado.id,
            id_usuario=usuario_creado.id,
            campo_cambiado=None,
            fecha_cambio=datetime.now(),
            valor_anterior=None,
            valor_nuevo=None,
            accion="creado"
        ))
        
        return InformacionUsuario.model_validate(usuario_creado)
        

    def login(self, payload: LoginRequest) -> TokenResponse:
        #buscar
        usuario = self.usuario_repo.get_usuario_by_email(payload.email)
        
        #validar credenciales
        if not usuario or not verify_password(payload.password, usuario.password):
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