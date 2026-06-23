from sqlmodel import Session, select, delete
from app.models.comentario import Comentario

class ComentarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_comentario_by_id(self, id_comentario: int) -> Comentario | None:
        return self.db.get(Comentario, id_comentario)
    
    def get_comentario_by_ticket(self, id_ticket: int) -> list[Comentario]:
        query = select(Comentario).where(Comentario.id_ticket == id_ticket)
        return self.db.exec(query).all()
    
    def get_comentario_by_usuario(self, id_usuario: int) -> list[Comentario]:
        query = select(Comentario).where(Comentario.id_usuario == id_usuario)
        return self.db.exec(query).all()
    
    def crear_comentario(self, comentario: Comentario) -> Comentario:
        self.db.add(comentario)
        self.db.commit()
        self.db.refresh(comentario)
        return comentario
    
    def actualizar_comentario(self, comentario: Comentario) -> Comentario:
        self.db.commit()
        self.db.refresh(comentario)
        return comentario
    
    def eliminar_comentario(self, id_comentario: int) -> None:
        self.db.exec(delete(Comentario).where(Comentario.id == id_comentario))
        self.db.commit()

    def ultimo_comentario(self, id_ticket: int) -> bool:
        query = select(Comentario).where(Comentario.id_ticket == id_ticket).order_by(Comentario.id.desc()).limit(1)
        return self.db.exec(query).one()