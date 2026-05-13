from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session
from app.models.ticket import ActualizarTicket, CrearTicket, Ticket
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio


class TicketService:
    def __init__(self, db: Session):
        self.usuario = UsuarioRepositorio(db)
        self.repo = TicketRepositorio(db)
        
    def ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        usuario = self.usuario.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"No se encontro el usuario {id_usuario}")
        
        return self.repo.get_ticket_by_usuario(id_usuario)
        
    def ticket_by_id(self, id_ticket: int) -> Ticket | None:
        ticket =  self.repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        return ticket
    
    def listar_tickets(self) -> list[Ticket]:
        return self.repo.listar_tickets()
    
    def crear_ticket(self, id_usuario: int, payload: CrearTicket) -> Ticket:
        usuario = self.usuario.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"No se encontro el usuario {id_usuario}")
        
        ticket = Ticket(**payload.model_dump())
        ticket.id_usuario = id_usuario
        
        return self.repo.crear_ticket(ticket)
    
    def actualizar_ticket(self, id_ticket: int, payload: ActualizarTicket) -> Ticket:
        ticket = self.repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        actualizar = payload.model_dump(exclude_unset=True)
        
        for key, value in actualizar.items():
            setattr(ticket, key, value)
        
        ticket.fecha_actualizacion = datetime.now()
        self.repo.actualizar_ticket(ticket)
        
        return ticket
