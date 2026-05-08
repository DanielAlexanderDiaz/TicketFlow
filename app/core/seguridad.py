import datetime
import jwt
from pwdlib import PasswordHash
from app.core.config import configuracion

pwd_context = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def crear_token(data: dict, tiempo_expiracion: int | None = None) -> str:
    codificar = data.copy()
    expiracion = datetime.datetime.utcnow() + datetime.timedelta(minutes=tiempo_expiracion or configuracion.JWT_TIEMPO_EXPIRACION)
    codificar.update({"exp": expiracion})
    return jwt.encode(codificar, configuracion.JWT_SECRET_KEY, algorithm=configuracion.JWT_ALGORITMO)
    
def decoder_token(token: str) -> dict:
    return jwt.decode(token, configuracion.JWT_SECRET_KEY, algorithms=[configuracion.JWT_ALGORITMO])