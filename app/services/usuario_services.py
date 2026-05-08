from sqlmodel import Session

from app.repositories.usuario_repository import UsuarioRepositorio


class usuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepositorio(db)
        
    def listar_usuario(self, id_usuario: int):
        return self.repo.get_usuario_by_id(id_usuario)