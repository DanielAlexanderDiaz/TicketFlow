from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import ticket
from app.models.auditoria import Auditoria
from app.models.compartir_ticket import TicketCompartir
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.compartir import InfoCompartir
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio


class CompartirServicie:
    def __init__(self, db: Session):
        self.db = db
        self.compartir_repo = CompartirRepository(db)
        self.ticket_repo = TicketRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def compartir_ticket(self, id_ticket: int, id_propietario: int, id_compartido: int) -> InfoCompartir:
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el ticket")
        
        es_propietario = ticket.id_usuario == id_propietario
        if not es_propietario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No es propietario del ticket")
        
        usuario_compartir_existe = self.ticket_repo.get_ticket_by_id(id_compartido)
        if not usuario_compartir_existe:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el usuario compartido")
        
        compartir = TicketCompartir(
            id_ticket = id_ticket, 
            id_usuario_propietario = id_propietario, 
            id_usuario_compartido = id_compartido)
        
        self.compartir_repo.compartir_ticket(compartir)
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "compartir ticket",
            id_entidad = id_ticket, 
            id_usuario = id_propietario,
            id_usuario_compartido = id_compartido,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior=None,
            valor_nuevo="Ticket compartido",
            accion="compartir"
        ))
    
        return InfoCompartir.model_validate(compartir)
        
        
        
    # def compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, payload: SolicitudCompartir) -> InfoCompartir:
    #     ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
    #     if not ticket:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el ticket")
    #     es_propietario = ticket.id_usuario == id_usuario_propietario
    #     if not es_propietario:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el ticket")
        
    #     compartir = self.compartir_repo.compartir_ticket(TicketCompartir(id_ticket, id_usuario_propietario, id_usuario_compartido))
        
    #     self.auditoria_repo.crear_audtoria(Auditoria(
    #         entidad = "compartir",
    #         id_entidad = ticket.id, 
    #         id_usuario = id_usuario_propietario,
    #         id_usuario_compartido = id_usuario_compartido,
    #         campo_cambiado="*",
    #         fecha_cambio=datetime.now(),
    #         valor_anterior=None,
    #         valor_nuevo="Ticket compartido",
    #         accion="compartir"
    #     ))
        
    #     return InfoCompartir.model_validate(compartir)
    
    # def remover_compartir_ticket(self, id_ticket: int, id_usuario_propietario: int, id_usuario_compartido: int) -> InfoCompartir:
    #     ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
    #     if not ticket:
    #         raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
    #     es_propietario = ticket.id_usuario == id_usuario_propietario
    #     if not es_propietario:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        
    #     compartir = self.compartir_repo.remover_compartir_ticket(id_ticket, id_usuario_compartido)
                
    #     self.auditoria_repo.crear_audtoria(Auditoria(
    #         entidad = "compartir",
    #         id_entidad = ticket.id, 
    #         id_usuario = id_usuario_propietario,
    #         id_usuario_compartido = id_usuario_compartido,
    #         campo_cambiado="*",
    #         fecha_cambio=datetime.now(),
    #         valor_anterior="Ticket compartido",
    #         valor_nuevo="Ticket no compartido",
    #         accion="remover"
    #     ))
        
    #     return InfoCompartir.model_validate(compartir)