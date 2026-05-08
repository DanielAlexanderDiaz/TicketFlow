from sqlmodel import Session
from app.models.ticket import CrearTicket, Ticket
from app.repositories.ticket_repository import TicketRepositorio


class TicketService:
    def __init__(self, db: Session):
        self.repo = TicketRepositorio(db)
        
    def ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        return self.repo.get_ticket_by_usuario(id_usuario)
    
    def ticket_by_id(self, id_ticket: int) -> Ticket | None:
        return self.repo.get_ticket_by_id(id_ticket)
    
    def crear_ticket(self, payload: CrearTicket) -> Ticket:
        return self.repo.crear_ticket(payload)
    
