from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencias import DBSession
from app.models.usuario import CrearUsuario, InfoUsuario
from app.repositories.usuario_repository import UsuarioRepositorio
from app.services.auth_services import AuthServices

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=InfoUsuario, status_code=status.HTTP_201_CREATED)
def registrar(payload: CrearUsuario, db: DBSession):
    servicio = AuthServices(UsuarioRepositorio(db))
    return servicio.registrar(payload)

@router.post("/login")
def login(email: str, password: str, db: DBSession):
    servicio = AuthServices(UsuarioRepositorio(db))
    token = servicio.login(email, password)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/token")
def login(db: DBSession, form: OAuth2PasswordRequestForm = Depends()):
    email = form.username
    password = form.password
    servicio = AuthServices(UsuarioRepositorio(db))
    token = servicio.login(email, password)
    return {"access_token": token, "token_type": "bearer"}