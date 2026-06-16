from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.schemas.compartir import InformacionCompartir
from app.services.compartir_services import CompartirServicie


router = APIRouter(prefix="/compartir", tags=["compartir"])
