from datetime import datetime
from math import ceil
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.auditoria import Auditoria
from app.models.ticket import Ticket
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.ticket import ActualizarTickekActivo, ActualizarTicket, CrearTicket, HistorialTicket, InfoTicket, PaginacionTicket
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.utils.uploads_file import save_uploaded_img


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.usuario_repo = UsuarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def ticket_by_usuario(self, id_usuario: int) -> list[InfoTicket]:
        # validar
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el usuario {id_usuario}")
        
        # Ticket que se comparten
        compartidos = self.compartir_repo.listar_tickets_compartidos(id_usuario)
        ids_compartidos = [c.id_ticket for c in compartidos]
        
        # ids de tickets
        tickets_compartidos = self.ticket_repo.lista_ids_ticket(ids_compartidos)
        
        # Tickets propios
        tickets_propios = self.ticket_repo.get_ticket_by_usuario(id_usuario)
        
        combinar = {t.id: t for t in tickets_propios}
        for t in tickets_compartidos:
            combinar.setdefault(t.id, t)
            
        ordenado = sorted(combinar.values(), key=lambda t: t.id, reverse=True)
        return [InfoTicket.model_validate(t) for t in ordenado]
               
    def ticket_by_id(self, id_ticket: int, id_usuario: int) -> InfoTicket:
        # validar
        ticket =  self.ticket.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        # valida si es propietario o compartido
        es_propietario = ticket.id_usuario == id_usuario
        tiene_compartidos = self.compartir_repo.tiene_ticket_compartido(id_ticket, id_usuario)
        if not es_propietario and not tiene_compartidos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        
        return InfoTicket.model_validate(ticket)   
    
    def listar_tickets(self) -> list[Ticket]:
        tickets = self.ticket.listar_tickets()
        return [InfoTicket.model_validate(t) for t in tickets] 
    
    def crear_ticket(self, id_usuario: int, payload: CrearTicket) -> InfoTicket:
        # validar
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el usuario {id_usuario}")
        
        # Crear el ticket
        ticket = Ticket(**payload.model_dump())
        ticket.id_usuario = id_usuario
        ticket.fecha_creacion = datetime.now()
        ticket.fecha_actualizacion = ticket.fecha_creacion

        # Guardar el ticket
        ticket_guardado = self.ticket_repo.crear_ticket(ticket)
        
        # Guardar auditoria
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = ticket_guardado.id, 
            id_usuario = id_usuario,
            id_usuario_compartido = None,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="Creacion de ticket",
            accion="creado"
            ))
        
        return InfoTicket.model_validate(ticket_guardado)
    
    def actualizar_ticket(self, id_ticket: int, payload: ActualizarTicket, id_usuario: int) -> InfoTicket:
        # validar
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")

        # valida si es propietario o compartido
        es_propietario = ticket.id_usuario == id_usuario
        tiene_acceso = self.compartir_repo.tiene_ticket_compartido(id_ticket, id_usuario)
        if not es_propietario and not tiene_acceso:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el ticket {id_ticket}")

        if payload.imagen_url:
            img_data = save_uploaded_img(payload.imagen_url)
            ticket.imagen_url = img_data["url"]

        datos = payload.model_dump(exclude_unset=True, exclude_none=True, exclude={"imagen_url"})
        if not datos and not payload.imagen_url:
            return InfoTicket.model_validate(ticket)

        # obtener valores anteriores
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(ticket, campo, None)
            setattr(ticket, campo, nuevo_valor)

            if str(valor_anterior) != str(nuevo_valor):
                self.auditoria_repo.crear_audtoria(Auditoria(
                    entidad = "ticket",
                    id_entidad = id_ticket,
                    id_usuario = id_usuario,
                    id_usuario_compartido = None,
                    campo_cambiado=campo,
                    fecha_cambio=datetime.now(),
                    valor_anterior=str(valor_anterior),
                    valor_nuevo=str(nuevo_valor),
                    accion="actualizado"
                    ))

        ticket.fecha_actualizacion = datetime.now()
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)

        return InfoTicket.model_validate(ticket_actualizado)

    def actualizar_ticket_activo(self, id_ticket: int, id_usuario: int, payload: ActualizarTickekActivo) -> InfoTicket:
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")
        
        # valida si es propietario o compartido
        es_propietario = ticket.id_usuario == id_usuario
        if not es_propietario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el ticket {id_ticket}")
        
        valor_anterior = ticket.activo
        nuevo_valor = payload.activo
        
        ticket.activo = payload.activo
        
        if str(valor_anterior) != str(nuevo_valor):
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "ticket",
                id_entidad = id_ticket, 
                id_usuario = id_usuario,
                id_usuario_compartido = None,
                campo_cambiado="activo",
                fecha_cambio=datetime.now(),
                valor_anterior=str(valor_anterior),
                valor_nuevo=str(nuevo_valor),
                accion="actualizado"
                ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
        return InfoTicket.model_validate(ticket_actualizado)

    def obtener_historial(self, id_ticket: int) -> list[HistorialTicket]:
        # validar
        ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
        registros = self.ticket_repo.get_ticket_historial(id_ticket)
        return [HistorialTicket.model_validate(h) for h in registros]
    
    def listar_ticket_paginado(
        self,
        estado = None,
        prioridad = None,
        activo = None,
        titulo = None,
        page: int = 1,
        size: int = 10
    ):
        skip = (page - 1) * size
        tickets, total = self.ticket_repo.listar_ticket_filtro(
            estado, 
            prioridad, 
            activo, 
            titulo, 
            skip, 
            size)
        
        return {
            "items": [InfoTicket.model_validate(t) for t in tickets],
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size)
        }
            
        