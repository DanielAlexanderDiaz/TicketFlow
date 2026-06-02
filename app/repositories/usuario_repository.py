from pydantic import EmailStr
from sqlmodel import Session, select
from app.models.usuario import Usuario

class UsuarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_usuario_by_id(self, id_usuario: int) -> Usuario | None:
        return self.db.get(Usuario, id_usuario)

    def get_usuario_by_email(self, email: EmailStr) -> Usuario | None:
        query = select(Usuario).where(Usuario.email == email)
        return self.db.exec(query).first()       
    
    def listar_usuarios(self) -> list[Usuario] | None:
        query = select(Usuario)
        return self.db.exec(query).all()
    
    def crear_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def eliminar_usuario(self, usuario: Usuario) -> bool:
        self.db.delete(usuario)
        self.db.commit()
        return True