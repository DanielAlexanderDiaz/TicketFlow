from sqlalchemy import func
from sqlmodel import Session, desc, select, delete
from app.models.ticket import EstadoTicket, PrioridadTicket, Ticket
from typing import Optional

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
    
    def eliminar_ticket(self, id_ticket: int) -> None:
        query = delete(Ticket).where(Ticket.id == id_ticket)
        self.db.exec(query)
        self.db.commit()
    
    def lista_ids_ticket(self, ids: list[int]) -> list[Ticket]:
        if not ids:
            return []
        query = select(Ticket).where(Ticket.id.in_(ids))
        return self.db.exec(query).all()
    
    def listar_ticket_filtro(
        self,
        estado: Optional[EstadoTicket] = None,
        prioridad: Optional[PrioridadTicket] = None,
        activo: Optional[bool] = None,
        titulo: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
        ) -> tuple[list[Ticket], int]: 
        query = select(Ticket)
        count_query = select(func.count(Ticket.id))
        
        if estado is not None:
            query = query.where(Ticket.estado == estado)
            count_query = count_query.where(Ticket.estado == estado)
        if prioridad is not None:
            query = query.where(Ticket.prioridad == prioridad)
            count_query = count_query.where(Ticket.prioridad == prioridad)
        if activo is not None:
            query = query.where(Ticket.activo == activo)
            count_query = count_query.where(Ticket.activo == activo)
        if titulo is not None:
            like_pattern = f"%{titulo}%"
            query = query.where(Ticket.titulo.ilike(like_pattern))
            count_query = count_query.where(Ticket.titulo.ilike(like_pattern))
        
        query = query.order_by(desc(Ticket.id))
        
        total = self.db.exec(count_query).one()
        items = self.db.exec(query.offset(skip).limit(limit)).all()
        return items, total