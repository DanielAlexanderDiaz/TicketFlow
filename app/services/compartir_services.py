from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.ticket import TicketAuditoria
from app.schemas.compartir import InfoCompartir
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio


class CompartirServicie:
    def __init__(self, db: Session):
        self.db = db
        self.compartir_repo = CompartirRepository(db)
        self.ticket_repo = TicketRepositorio(db)
        
        
    def compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int) -> InfoCompartir:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        es_propietario = ticket.id_usuario == id_usuario_propietario
        if not es_propietario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        
        compartir = self.compartir_repo.compartir_ticket(id_ticket, id_usuario_compartido)
        
        self.ticket_repo.crear_audtoria(TicketAuditoria(
            id_ticket=ticket.id, 
            id_usuario=id_usuario_propietario, 
            id_usuario_compartido=id_usuario_compartido,
            campo_cambiado="*", 
            valor_anterior=None,
            valor_nuevo="Ticket compartido",
            accion = "compartido"
        ))
        
        return InfoCompartir.model_validate(compartir)
    
    def remover_compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int) -> InfoCompartir:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        es_propietario = ticket.id_usuario == id_usuario_propietario
        if not es_propietario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        
        compartir = self.compartir_repo.remover_compartir_ticket(id_ticket, id_usuario_compartido)
                
        self.ticket_repo.crear_audtoria(TicketAuditoria(
            id_ticket=ticket.id, 
            id_usuario=id_usuario_propietario, 
            id_usuario_compartido=id_usuario_compartido,
            campo_cambiado="*", 
            valor_anterior="ticket compartido",
            valor_nuevo="ticket no compartido",
            accion = "remover"
        ))
        
        return InfoCompartir.model_validate(compartir)