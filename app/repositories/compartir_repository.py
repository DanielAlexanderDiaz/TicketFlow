from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, delete, select
from app.models.compartir_ticket import TicketCompartir
from app.schemas.compartir import CompartirTicket


class CompartirRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def todos_compartidos_ticket(self, id_ticket: int ) -> list[TicketCompartir]:
        query = select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket)
        return self.db.exec(query).all()
    
    def ticket_compartido(self, id_ticket: int) -> bool:  
        resultado = self.db.exec(select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket)).first()
        return resultado is not None
        
    def usuario_tiene_ticket_compartido(self, id_ticket: int, id_usuario_destino: int) -> bool:
        resultado = self.db.exec(select(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket).where(TicketCompartir.id_usuario_destino == id_usuario_destino)).first()
        return resultado is not None
        
    def compartir_ticket(self, compartir: TicketCompartir) -> TicketCompartir:
        self.db.add(compartir)
        self.db.commit()
        self.db.refresh(compartir)
        
        return compartir

    def eliminar_compartir_ticket(self, id_ticket: int, id_usuario_destino: int):
        self.db.exec(delete(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket).where(TicketCompartir.id_usuario_destino == id_usuario_destino))
        self.db.commit()
        
    def eliminar_todos_compartidos(self, id_ticket: int):
        self.db.exec(delete(TicketCompartir).where(TicketCompartir.id_ticket == id_ticket))
        self.db.commit()
        
    def tickets_compartidos_con_usuario(self, id_usuario_destino: int) -> list[int]:
        query = select(TicketCompartir.id_ticket).where(TicketCompartir.id_usuario_destino == id_usuario_destino)
        return self.db.exec(query).all()
    
    def ids_tickets_compartidos_por_usuario_origen(self, id_usuario_origen: int) -> list[int]:
        query = select(TicketCompartir.id_ticket).where(TicketCompartir.id_usuario_origen == id_usuario_origen)
        return self.db.exec(query).all()
    
    def buscar_compartidos(self, 
                           ids_permitidos: Optional[set[int]],
                           id_ticket: Optional[int],
                           id_usuario_origen: Optional[int],
                           id_usuario_destino: Optional[int],
                           fecha_creacion: Optional[datetime],
                           orden: str,
                           direccion: str,
                           limit: int,
                           offset: int
                        )-> tuple[int, list[CompartirTicket]]:
        stmt = select(TicketCompartir)
        
        if ids_permitidos is not None:
            if not ids_permitidos:
                return 0, []
            stmt = stmt.where(TicketCompartir.id_ticket.in_(ids_permitidos))
        
        if id_ticket is not None:
            stmt = stmt.where(TicketCompartir.id_ticket == id_ticket)
        if id_usuario_origen is not None:
            stmt = stmt.where(TicketCompartir.id_usuario_origen == id_usuario_origen)
        if id_usuario_destino is not None:
            stmt = stmt.where(TicketCompartir.id_usuario_destino == id_usuario_destino)
        if fecha_creacion is not None:
            stmt = stmt.where(TicketCompartir.fecha_creacion == fecha_creacion)
        
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if total == 0:
            return 0, []
        
        columnas_orden = {
            "id": TicketCompartir.id,
            "id_ticket": TicketCompartir.id_ticket,
            "id_usuario_origen": TicketCompartir.id_usuario_origen,
            "id_usuario_destino": TicketCompartir.id_usuario_destino,
            "fecha_creacion": TicketCompartir.fecha_creacion
        }
        
        orden_col = columnas_orden.get(orden, TicketCompartir.id)
        stmt = stmt.order_by(orden_col.asc() if direccion == "asc" else orden_col.desc())
        
        items = self.db.exec(stmt.offset(offset).limit(limit)).all()
        return total, items