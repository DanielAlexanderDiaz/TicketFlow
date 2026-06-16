from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.api.dependencias import DBSession
from app.schemas.usuario import LoginRequest, InformacionUsuario, Registro
from app.repositories.usuario_repository import UsuarioRepositorio
from app.services.auth_services import AuthServices

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=InformacionUsuario, status_code=status.HTTP_201_CREATED)
def registrar(payload: Registro, db: DBSession):
    servicio = AuthServices(db)
    return servicio.registrar(payload)

@router.post("/login")
def login(payload: LoginRequest, db: DBSession):
    servicio = AuthServices(db)
    token_response = servicio.login(payload)
    return {"access_token": token_response.access_token, "token_type": "bearer"}

@router.post("/token")
def login(db: DBSession, form: OAuth2PasswordRequestForm = Depends()):
    payload = LoginRequest(email=form.username, password=form.password)
    servicio = AuthServices(db)
    token_response = servicio.login(payload)
    return {"access_token": token_response.access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession):
    servicio = AuthServices(db)
    servicio.logout(token)