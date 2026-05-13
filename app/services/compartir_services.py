from sqlmodel import Session
from app.models.compartir_ticket import TicketCompartir
from app.repositories.compartir_repository import CompartirRepository
from app.services.ticket_services import TicketService


class CompartirServicie:
    def __init__(self, db: Session):
        self.compartir_ticket = CompartirRepository(db)
        self.ticket = TicketService(db)
        
