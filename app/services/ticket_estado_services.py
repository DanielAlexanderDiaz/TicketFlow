from sqlmodel import Session
from app.models.ticket import EstadoTicket
from app.repositories.ticket_repository import TicketRepositorio
from app.schemas.ticket import ActualizarEstadoTicket, InfoTicket

TRANSICIONES_PERMITIDAS = {
    EstadoTicket.PENDIENTE: [EstadoTicket.EN_PROGRESO],
    EstadoTicket.EN_PROGRESO: [EstadoTicket.FINALIZADO],
    EstadoTicket.FINALIZADO: []
}

class TicketEstadoServices:
    
    def __init__(self, db: Session):
        self.db = db
        self.ticket_repo = TicketRepositorio(db)
    
    @staticmethod
    def puede_transicionar(actual: EstadoTicket, nuevo: EstadoTicket):
        return nuevo in TRANSICIONES_PERMITIDAS.get(actual, [])
    
    @staticmethod
    def transicionar(ticket, new_estado: EstadoTicket):
        if not TicketEstadoServices.puede_transicionar(ticket.estado, new_estado):
            raise ValueError(f"No es posible pasar de {ticket.estado} a {new_estado}.")
        
        ticket.estado = new_estado
        
        return ticket
    
    def cambiar_estado_ticket(self, id_ticket: int, new_estado: ActualizarEstadoTicket) -> InfoTicket:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise ValueError(f"No se encontro el ticket {id_ticket}")
        
        ticket = self.transicionar(ticket, new_estado.estado)
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)

        return InfoTicket.model_validate(ticket_actualizado)