from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session
from app.models.ticket import ActualizarTicket, CrearTicket, HistorialTicket, Ticket, TicketAuditoria
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio


class TicketService:
    def __init__(self, db: Session):
        self.usuario = UsuarioRepositorio(db)
        self.ticket = TicketRepositorio(db)
        self.compartir = CompartirRepository(db)
        
    def ticket_by_usuario(self, id_usuario: int) -> list[Ticket]:
        usuario = self.usuario.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"No se encontro el usuario {id_usuario}")
        
        registros_compartidos = self.compartir.listar_tickets_compartidos(id_usuario)
        ids_compartidos = [reg.id_ticket for reg in registros_compartidos]
        
        tickets_compartidos = self.ticket.lista_ids_ticket(ids_compartidos)
        
        tickets_propios = self.ticket.get_ticket_by_usuario(id_usuario)
        
        combinar = {ticket.id: ticket for ticket in tickets_propios}
        for ticket in tickets_compartidos:
            combinar.setdefault(ticket.id, ticket)
            
        return sorted(combinar.values(), key=lambda t: t.id, reverse=True)
        
        
        
    def ticket_by_id(self, id_ticket: int) -> Ticket | None:
        ticket =  self.ticket.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        return ticket
    
    def listar_tickets(self) -> list[Ticket]:
        return self.ticket.listar_tickets()
    
    def crear_ticket(self, id_usuario: int, payload: CrearTicket) -> Ticket:
        usuario = self.usuario.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"No se encontro el usuario {id_usuario}")
        
        ticket = Ticket(**payload.model_dump())
        ticket.id_usuario = id_usuario
        ticket.fecha_creacion = datetime.now()

        # Guardar el ticket
        ticket = self.ticket.crear_ticket(ticket)
        
        # Guardar auditoria
        self.ticket.crear_audtoria(TicketAuditoria(
            id_ticket=ticket.id, 
            id_usuario=id_usuario, 
            campo_cambiado="*", 
            valor_anterior=None,
            valor_nuevo="Ticket creado",
            accion = "creado"
            ))
        
        return ticket
    
    def actualizar_ticket(self, id_ticket: int, payload: ActualizarTicket, id_usuario: int) -> Ticket:
        ticket = self.ticket.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        actualizar = payload.model_dump(exclude_unset=True)
        
        for key, value in actualizar.items():
            old_value = getattr(ticket, key)
            setattr(ticket, key, value)
            
        # Guardar auditoria
        if str(old_value) != str(value):
            self.ticket.crear_audtoria(TicketAuditoria(
                id_ticket=ticket.id, 
                id_usuario=id_usuario, 
                campo_cambiado=key, 
                valor_anterior=str(old_value),
                valor_nuevo=str(value),
                accion = "actualizado"
                ))
        
        ticket.fecha_actualizacion = datetime.now()
        self.ticket.actualizar_ticket(ticket)
        
        return ticket

    def obtener_historial(self, id_ticket: int) -> list[HistorialTicket]:
        return self.ticket.get_ticket_historial(id_ticket)