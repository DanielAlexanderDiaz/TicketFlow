from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencias import DBSession
from app.schemas.usuario import LoginRequest, InfoUsuario, LoginRequest
from app.repositories.usuario_repository import UsuarioRepositorio
from app.services.auth_services import AuthServices

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=InfoUsuario, status_code=status.HTTP_201_CREATED)
def registrar(payload: LoginRequest, db: DBSession):
    servicio = AuthServices(UsuarioRepositorio(db))
    return servicio.registrar(payload)

@router.post("/login")
def login(payload: LoginRequest, db: DBSession):
    servicio = AuthServices(UsuarioRepositorio(db))
    token_response = servicio.login(payload)
    return {"access_token": token_response.access_token, "token_type": "bearer"}

@router.post("/token")
def login(db: DBSession, form: OAuth2PasswordRequestForm = Depends()):
    payload = LoginRequest(email=form.username, password=form.password)
    servicio = AuthServices(UsuarioRepositorio(db))
    token_response = servicio.login(payload)
    return {"access_token": token_response.access_token, "token_type": "bearer"}