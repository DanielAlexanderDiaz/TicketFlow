from typing import Optional
from sqlalchemy import func
from sqlmodel import Session, desc, select, delete
from app.models.ticket import Ticket

class TicketRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_ticket_by_id(self, id_ticket: int) -> Ticket | None:
        return self.db.get(Ticket, id_ticket)
    
    def get_ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        return self.db.exec(select(Ticket).where(Ticket.id_usuario_creador == id_usuario)).all()
    
    def listar_todos_tickets(self) -> list[Ticket]:
        return self.db.exec(select(Ticket)).all()
    
    def crear_ticket(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def actualizar_ticket(self, ticket: Ticket) -> Ticket:
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def eliminar_ticket(self, id_ticket: int) -> None:
        self.db.exec(delete(Ticket).where(Ticket.id == id_ticket))
        self.db.commit()
        
    def contar_tickets(self) -> int:
        return self.db.exec(select(func.count(Ticket.id))).scalar()
        
    def buscar_ticket(self, query: Optional[str], orden: str, direccion: str, limit: int, offset: int) -> tuple[int, list[Ticket]]:
        stmt = select(Ticket)
        if query:
            stmt = stmt.where(Ticket.titulo(f"%{query}%"))
            
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if total == 0:
            return 0, []
        
        orden_col = Ticket.id if orden == "id" else func.lower(Ticket.titulo)
        stmt = stmt.order_by(orden_col.asc() if direccion == "asc" else orden_col.desc())
        items = self.db.exec(stmt.limit(limit).offset(offset)).all()
        return total, items
    
    