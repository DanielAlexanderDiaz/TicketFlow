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