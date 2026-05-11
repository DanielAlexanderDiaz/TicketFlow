from sqlmodel import Session, select
from app.models.comentario import Comentario

class ComentarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_comentario_by_id(self, id_comentario: int) -> Comentario | None:
        return self.db.get(Comentario, id_comentario)
    
    def get_comentario_by_ticket(self, id_ticket: int) -> Comentario | None:
        return self.db.exec(select(Comentario).where(Comentario.id_ticket == id_ticket)).first()
    
    def crear_comentario(self, comentario: Comentario) -> Comentario:
        self.db.add(comentario)
        self.db.commit()
        self.db.refresh(comentario)
        return comentario
    
    def actualizar_comentario(self, comentario: Comentario) -> Comentario:
        # self.db.add(comentario)
        self.db.commit()
        self.db.refresh(comentario)
        return comentario