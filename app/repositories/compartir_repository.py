from sqlmodel import Session, delete, select
from app.models.compartir_ticket import TicketCompartir


class CompartirRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def ticket_compartido(self, id_ticket: int) -> bool:  
        query = select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket)  
        query = self.db.exec(query).first()
        
        return True
        
    def usuario_tiene_ticket_compartido(self, id_ticket: int, id_usuario_compartido: int) -> bool:
        query = select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket and (TicketCompartir.id_usuario_destino == id_usuario_compartido))  
        query = self.db.exec(query).first()
        
        return True
        
    def compartir_ticket(self, compartir: TicketCompartir) -> TicketCompartir:
        self.db.add(compartir)
        self.db.commit()
        self.db.refresh(compartir)
        
        return compartir
    
    def eliminar_compartir_ticket(self, id_ticket: int):
        query = delete(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket)
        self.db.exec(query)
        self.db.commit()