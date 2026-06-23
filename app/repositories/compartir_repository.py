from sqlmodel import Session, delete, select
from app.models.compartir_ticket import TicketCompartir


class CompartirRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def ticket_compartido(self, id_ticket: int) -> bool:  
        resultado = self.db.exec(select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket)).first()
        return resultado is not None
        
    def usuario_tiene_ticket_compartido(self, id_ticket: int, id_usuario_compartido: int) -> bool:
        resultado = self.db.exec(select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket).where(TicketCompartir.id_usuario_destino == id_usuario_compartido)).first()
        return resultado is not None
        
    def compartir_ticket(self, compartir: TicketCompartir) -> TicketCompartir:
        self.db.add(compartir)
        self.db.commit()
        self.db.refresh(compartir)
        
        return compartir

    def eliminar_compartir_ticket(self, id_ticket: int, id_usuario_compartido: int):
        self.db.exec(delete(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket).where(TicketCompartir.id_usuario_destino == id_usuario_compartido))
        self.db.commit()