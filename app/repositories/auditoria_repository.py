from select import select
from sqlmodel import Session
from app.models.auditoria import Auditoria


class AuditoriaRepositorio:
    def __init__(self, db: Session):
        self.db = db
    
    def crear_audtoria(self, auditoria: Auditoria) -> Auditoria:
        self.db.add(auditoria)
        self.db.commit()
        self.db.refresh(auditoria)
        return auditoria
    
    def get_ticket_historial(self, id_ticket: int) -> list[Auditoria]:
        query = select(Auditoria).where(Auditoria.id_entidad == id_ticket)
        return self.db.exec(query).all()