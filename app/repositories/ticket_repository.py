from sqlmodel import Session, select
from app.models.ticket import Ticket

class TicketRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_ticket_by_id(self, id_ticket: int) -> Ticket | None:
        return self.db.get(Ticket, id_ticket)
    
    def get_ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        query = select(Ticket).where(Ticket.id_usuario == id_usuario)
        return self.db.exec(query).all()
    
    def listar_todos_tickets(self) -> list[Ticket]:
        query = select(Ticket)
        return self.db.exec(query).all()
    
    def crear_ticket(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def actualizar_ticket(self, ticket: Ticket) -> Ticket:
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def lista_ids_ticket(self, ids: list[int]) -> list[Ticket]:
        if not ids:
            return []
        query = select(Ticket).where(Ticket.id.in_(ids))
        return self.db.exec(query).all()
    
    # def crear_audtoria(self, auditoria: TicketAuditoria) -> TicketAuditoria:
    #     self.db.add(auditoria)
    #     self.db.commit()
    #     self.db.refresh(auditoria)
    #     return auditoria
    
    # def get_ticket_historial(self, id_ticket: int) -> list[TicketAuditoria]:
    #     query = select(TicketAuditoria).where(TicketAuditoria.id_ticket == id_ticket).order_by(TicketAuditoria.fecha_cambio.desc())
    #     return self.db.exec(query).all()
    
    