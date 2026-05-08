from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.core.db import get_session
from app.core.seguridad import decoder_token
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepositorio

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_db() -> Session:
    return next(get_session())

DBSession = Annotated[Session, Depends(get_db)]

def get_usuario_actual(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> Usuario:
    exepcion_credencial = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decoder_token(token)
        id_usuario = int(payload.get("sub"))
    except:
        raise exepcion_credencial
    
    repo = UsuarioRepositorio(db)
    usuario = repo.get_usuario_by_id(id_usuario)
    
    if not usuario:
        raise exepcion_credencial
    return usuario

UsuarioActual = Annotated[Usuario, Depends(get_usuario_actual)]