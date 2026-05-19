from sqlmodel import Session, delete
from app.models.compartir_ticket import TicketCompartir


class CompartirRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def compartir_ticket(self, compartir: TicketCompartir) -> TicketCompartir:
        self.db.add(compartir)
        self.db.commit()
        self.db.refresh(compartir)
        
        return compartir
    
    def eliminar_compartir_ticket(self, id_ticket: int):
        query = delete(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket)
        self.db.exec(query)
        self.db.commit()