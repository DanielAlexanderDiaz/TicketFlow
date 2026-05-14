from sqlmodel import Session, select, delete
from app.models.compartir_ticket import TicketCompartir


class CompartirRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def compartir_ticket(self, id_ticket: int, id_usuario: int) -> TicketCompartir:
        query = select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket, TicketCompartir.id_usuario == id_usuario)
        
        compartir = self.db.exec(query).first()
        
        if compartir:
            return compartir
        
        compartir = TicketCompartir(id_ticket=id_ticket, id_usuario=id_usuario)
        self.db.add(compartir)
        self.db.commit()
        self.db.refresh(compartir)
        
        return compartir
    
    def remover_compartir_ticket(self, id_ticket: int, id_usuario: int) -> None:
        query = delete(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket, TicketCompartir.id_usuario == id_usuario)
        compartir = self.db.exec(query).first()
        
        if compartir:
            self.db.delete(compartir)
            self.db.commit()
            
    def tiene_ticket_compartido(self, id_ticket: int, id_usuario: int) -> bool:
        query = select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket, TicketCompartir.id_usuario == id_usuario)
        compartir = self.db.exec(query).first()
        
        return True if compartir else False
    
    def listar_tickets_compartidos(self, id_usuario: int) -> list[int]:
        query = select(TicketCompartir).where(TicketCompartir.id_usuario == id_usuario)
        compartir = self.db.exec(query).all()
        
        return compartir