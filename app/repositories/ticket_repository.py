from sqlmodel import Session, select
from app.models.ticket import Ticket

class TicketRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_ticket_by_id(self, id_ticket: int) -> Ticket | None:
        return self.db.get(Ticket, id_ticket)
    
    def get_ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        return self.db.exec(select(Ticket).where(Ticket.id_usuario == id_usuario)).all()
    
    def listar_tickets(self) -> list[Ticket] | None:
        return self.db.exec(Ticket).all()
    
    def crear_ticket(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def actualizar_ticket(self, ticket: Ticket) -> Ticket:
        # self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    