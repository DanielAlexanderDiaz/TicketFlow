from fastapi import HTTPException
from sqlmodel import Session
from app.models.compartir_ticket import TicketCompartir
from app.models.ticket import TicketAuditoria
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio


class CompartirServicie:
    def __init__(self, db: Session):
        self.compartir = CompartirRepository(db)
        self.ticket = TicketRepositorio(db)
        
        
    def compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int):
        ticket = self.ticket.get_ticket_by_id(id_ticket)
        if not ticket or ticket.id_usuario != id_usuario_propietario:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        compartir = self.compartir.compartir_ticket(id_ticket, id_usuario_compartido)
        
        self.ticket.crear_audtoria(TicketAuditoria(
            id_ticket=ticket.id, 
            id_usuario=id_usuario_propietario, 
            id_usuario_compartido=id_usuario_compartido,
            campo_cambiado="*", 
            valor_anterior=None,
            valor_nuevo="Ticket compartido",
            accion = "compartido"
        ))
        
        return compartir
    
    def remover_compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int):
        ticket = self.ticket.get_ticket_by_id(id_ticket)
        if not ticket or ticket.id_usuario != id_usuario_propietario:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        compartir = self.compartir.remover_compartir_ticket(id_ticket, id_usuario_compartido)
                
        self.ticket.crear_audtoria(TicketAuditoria(
            id_ticket=ticket.id, 
            id_usuario=id_usuario_propietario, 
            id_usuario_compartido=id_usuario_compartido,
            campo_cambiado="*", 
            valor_anterior="ticket compartido",
            valor_nuevo="ticket no compartido",
            accion = "remover"
        ))
        
        return compartir