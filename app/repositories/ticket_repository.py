from datetime import date
from typing import Optional
from sqlalchemy import func
from sqlmodel import Session, desc, or_, select, delete
from app.models.ticket import EstadoTicket, PrioridadTicket, Ticket

class TicketRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_ticket_by_id(self, id_ticket: int) -> Ticket | None:
        return self.db.get(Ticket, id_ticket)
    
    def get_ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        return self.db.exec(select(Ticket).where(Ticket.id_usuario_creador == id_usuario)).all()
    
    def listar_todos_tickets(self) -> list[Ticket]:
        return self.db.exec(select(Ticket)).all()
    
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
        self.db.exec(delete(Ticket).where(Ticket.id == id_ticket))
        self.db.commit()
        
    def contar_tickets_filtrados(self, query: Optional[str]) -> int:
        stmt = select(Ticket)
        if query:
            stmt = stmt.where(Ticket.titulo.ilike(f"%{query}%"))
        return self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        
    def ids_tickets_propios_o_asignados(self, id_usuario: int) -> list[int]:
        query = select(Ticket.id).where(or_(Ticket.id_usuario_creador == id_usuario, Ticket.asignado == id_usuario))
        return self.db.exec(query).all()
    
    def buscar_ticket(self,
                    ids_permitidos: Optional[set[int]],
                    buscar_titulo: Optional[str],
                    buscar_descripcion: Optional[str],
                    id_ticket: Optional[int],
                    prioridad: Optional[PrioridadTicket],
                    estado: Optional[EstadoTicket],
                    asignado: Optional[int],
                    fecha_desde: Optional[date],
                    fecha_hasta: Optional[date],
                    orden: str,
                    direccion: str,
                    limit: int,
                    offset: int,
                    ) -> tuple[int, list[Ticket]]:
        stmt = select(Ticket)
        
        if ids_permitidos is not None:
            if not ids_permitidos:
                return 0, []
            stmt = stmt.where(Ticket.id.in_(ids_permitidos))
            
        # Busqueda - Coincidencia parcial
        if buscar_titulo is not None:
            stmt = stmt.where(Ticket.titulo.ilike(f"%{buscar_titulo}%"))
        if buscar_descripcion is not None:
            stmt = stmt.where(Ticket.descripcion.ilike(f"%{buscar_descripcion}%"))
            
        # Filtros - Coincidencia exacta
        if id_ticket is not None:
            stmt = stmt.where(Ticket.id == id_ticket)
        if prioridad is not None:
            stmt = stmt.where(Ticket.prioridad == prioridad)
        if estado is not None:
            stmt = stmt.where(Ticket.estado == estado)
        if asignado is not None:
            stmt = stmt.where(Ticket.asignado == asignado)
        if fecha_desde is not None:
            stmt = stmt.where(Ticket.fecha_creacion >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(Ticket.fecha_creacion <= fecha_hasta)
            
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if total == 0:
            return 0, []
        
        # Ordenamiento
        columnas_orden = {
            "id": Ticket.id,
            "titulo": Ticket.titulo,
            "prioridad": Ticket.prioridad,
            "estado": Ticket.estado,
            "fecha_creacion": Ticket.fecha_creacion,
        }
        
        orden_col = columnas_orden.get(orden, Ticket.id)
        stmt = stmt.order_by(orden_col.asc() if direccion == "asc" else orden_col.desc())
        
        items = self.db.exec(stmt.limit(limit).offset(offset)).all()
        return total, items