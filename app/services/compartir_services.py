from fastapi import HTTPException
from sqlmodel import Session
from app.models.compartir_ticket import TicketCompartir
from app.repositories.compartir_repository import CompartirRepository
from app.services.ticket_services import TicketService


class CompartirServicie:
    def __init__(self, db: Session):
        self.compartir = CompartirRepository(db)
        self.ticket = TicketService(db)
        
    def compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int):
        ticket = self.ticket.ticket_by_id(id_ticket)
        if not ticket or ticket.id_usuario != id_usuario_propietario:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        compartir = self.compartir.compartir_ticket(id_ticket, id_usuario_compartido)
        
        return compartir
    
    def remover_compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int):
        ticket = self.ticket.ticket_by_id(id_ticket)
        if not ticket or ticket.id_usuario != id_usuario_propietario:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        compartir = self.compartir.remover_compartir_ticket(id_ticket, id_usuario_compartido)
        
        return compartir