from sqlmodel import Session
from app.models.usuario import Usuario

class UsuarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_usuario_by_id(self, id_usuario: int) -> Usuario | None:
        return self.db.get(Usuario, id_usuario)

    def get_usuario_by_email(self, email: str) -> Usuario | None:
        return self.db.get(Usuario, email)        
    
    def crear_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    