from datetime import datetime
from math import ceil
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import ticket
from app.models.auditoria import Auditoria
from app.models.ticket import TRANSICIONES_PERMITIDAS, EstadoTicket, Ticket
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.ticket import ActualizarTicket, AsignarTicket, CambioEstadoTicket, CompartirTicket, CrearTicket, InformacionTicket
from app.repositories.compartir_repository import CompartirRepository
from app.repositories.ticket_repository import TicketRepositorio
from app.repositories.usuario_repository import UsuarioRepositorio
from app.utils.uploads_file import save_uploaded_img


class TicketService:
    def __init__(self, db: Session):
        self.usuario_repo = UsuarioRepositorio(db)
        self.ticket_repo = TicketRepositorio(db)
        self.compartir_repo = CompartirRepository(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def crear_ticket(self, id_usuario: int, payload: CrearTicket) -> InformacionTicket:
        # validar
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el usuario {id_usuario}")
        
        # Crear el ticket
        ticket = Ticket(titulo=payload.titulo, 
                        descripcion=payload.descripcion)
        ticket.id_usuario = id_usuario

        # Guardar el ticket
        ticket_guardado = self.ticket_repo.crear_ticket(ticket)
        
        # Guardar auditoria
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = ticket_guardado.id, 
            id_usuario = id_usuario,
            campo_cambiado="*",
            fecha_cambio=datetime.now(),
            valor_anterior="*",
            valor_nuevo="Creacion de ticket",
            accion="creado"
            ))
        
        return InformacionTicket.model_validate(ticket_guardado)
    
    def actualizar_ticket(self, id_ticket: int, id_usuario: int, payload: ActualizarTicket) -> InformacionTicket:
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")

        es_propietario = ticket.id_usuario_creador = id_usuario
        tiene_acceso = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        if not es_propietario and not tiene_acceso:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el ticket {id_ticket}")

        if payload.imagen_url:
            img_data = save_uploaded_img(payload.imagen_url)
            ticket.imagen_url = img_data["url"]

        datos = payload.model_dump(exclude_unset=True, exclude_none=True, exclude={"imagen_url"})
        if not datos and not payload.imagen_url:
            return InformacionTicket.model_validate(ticket)

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

        return InformacionTicket.model_validate(ticket_actualizado)
    
    def eliminar_ticket(self, id_ticket: int, id_usuario: int) -> InformacionTicket:
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")

        es_propietario = ticket.id_usuario_creador = id_usuario
        tiene_acceso = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        if not es_propietario and not tiene_acceso:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el ticket {id_ticket}")
        
        ticket_eliminado = self.ticket_repo.eliminar_ticket(id_ticket)
        return InformacionTicket.model_validate(ticket_eliminado)
    
    @staticmethod
    def puede_transicionar_ticket(actual: EstadoTicket, nuevo: EstadoTicket):        
        return nuevo in TRANSICIONES_PERMITIDAS.get(actual, [])
    @staticmethod
    def transicionar_ticket(ticket: Ticket, new_estado: EstadoTicket):
        if not TicketService.puede_transicionar_ticket(ticket.estado, new_estado):
            raise ValueError(f"No es posible pasar de {ticket.estado} a {new_estado}.")
        
        ticket.estado = new_estado
        
        return ticket
    
    def cambio_estado_ticket(self, id_ticket: int, id_usuario: int, payload: CambioEstadoTicket) -> InformacionTicket:
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")

        es_propietario = ticket.id_usuario_creador = id_usuario
        tiene_acceso = self.compartir_repo.usuario_tiene_ticket_compartido(id_ticket, id_usuario)
        if not es_propietario and not tiene_acceso:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el ticket {id_ticket}")
    
        valor_anterior = ticket.estado
        valor_nuevo = payload.estado
    
        nuevo_ticket = self.transicionar_ticket(ticket, payload.estado)
        if not nuevo_ticket:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No es posible pasar de {ticket.estado} a {payload.estado}.")
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = id_ticket,
            id_usuario = id_usuario,
            campo_cambiado="estado",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(valor_nuevo),
            accion="actualizado"
        ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(nuevo_ticket)
        return InformacionTicket.model_validate(ticket_actualizado)
        
    def asignar_ticket(self, id_ticket: int, payload: AsignarTicket) -> InformacionTicket: 
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")
        
        valor_anterior = ticket.id_usuario_asignado
        valor_nuevo = payload.id_usuario
        
        ticket.id_usuario_asignado = payload.id_usuario
        
        self.auditoria_repo.crear_audtoria(Auditoria(
            entidad = "ticket",
            id_entidad = id_ticket,
            id_usuario = payload.id_usuario,
            campo_cambiado="id_usuario_asignado",
            fecha_cambio=datetime.now(),
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(valor_nuevo),
            accion="actualizado"
        ))
        
        ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
        return InformacionTicket.model_validate(ticket_actualizado)
    
    def compartir_ticket(self, id_ticket: int, payload: CompartirTicket) -> InformacionTicket:
        ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")
        
        
        
        
        
        
        
        
        
    # def ticket_by_usuario(self, id_usuario: int) -> list[InformacionTicket]:
    #     # validar
    #     usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
    #     if not usuario:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el usuario {id_usuario}")
        
    #     # Ticket que se comparten
    #     compartidos = self.compartir_repo.listar_tickets_compartidos(id_usuario)
    #     ids_compartidos = [c.id_ticket for c in compartidos]
        
    #     # ids de tickets
    #     tickets_compartidos = self.ticket_repo.lista_ids_ticket(ids_compartidos)
        
    #     # Tickets propios
    #     tickets_propios = self.ticket_repo.get_ticket_by_usuario(id_usuario)
        
    #     combinar = {t.id: t for t in tickets_propios}
    #     for t in tickets_compartidos:
    #         combinar.setdefault(t.id, t)
            
    #     ordenado = sorted(combinar.values(), key=lambda t: t.id, reverse=True)
    #     return [InformacionTicket.model_validate(t) for t in ordenado]
               
    # def ticket_by_id(self, id_ticket: int, id_usuario: int) -> InformacionTicket:
    #     # validar
    #     ticket =  self.ticket.get_ticket_by_id(id_ticket)
    #     if not ticket:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
    #     # valida si es propietario o compartido
    #     es_propietario = ticket.id_usuario == id_usuario
    #     tiene_compartidos = self.compartir_repo.tiene_ticket_compartido(id_ticket, id_usuario)
    #     if not es_propietario and not tiene_compartidos:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontro el ticket {id_ticket}")
        
    #     return InformacionTicket.model_validate(ticket)   
    
    # def listar_tickets(self) -> list[Ticket]:
    #     tickets = self.ticket.listar_tickets()
    #     return [InformacionTicket.model_validate(t) for t in tickets] 
    
    # def actualizar_ticket_activo(self, id_ticket: int, id_usuario: int, payload: ActualizarTickekActivo) -> InformacionTicket:
    #     ticket =  self.ticket_repo.get_ticket_by_id(id_ticket)
    #     if not ticket:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id_ticket} no encontrado")
        
    #     # valida si es propietario o compartido
    #     es_propietario = ticket.id_usuario == id_usuario
    #     if not es_propietario:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No se tiene permiso para actualizar el ticket {id_ticket}")
        
    #     valor_anterior = ticket.activo
    #     nuevo_valor = payload.activo
        
    #     ticket.activo = payload.activo
        
    #     if str(valor_anterior) != str(nuevo_valor):
    #         self.auditoria_repo.crear_audtoria(Auditoria(
    #             entidad = "ticket",
    #             id_entidad = id_ticket, 
    #             id_usuario = id_usuario,
    #             id_usuario_compartido = None,
    #             campo_cambiado="activo",
    #             fecha_cambio=datetime.now(),
    #             valor_anterior=str(valor_anterior),
    #             valor_nuevo=str(nuevo_valor),
    #             accion="actualizado"
    #             ))
        
    #     ticket_actualizado = self.ticket_repo.actualizar_ticket(ticket)
        
    #     return InformacionTicket.model_validate(ticket_actualizado)

    # def obtener_historial(self, id_ticket: int) -> list[HistorialTicket]:
    #     # validar
    #     ticket = self.ticket_repo.get_ticket_by_id(id_ticket)
    #     if not ticket:
    #         raise HTTPException(status_code=404, detail=f"No se encontro el ticket {id_ticket}")
        
    #     registros = self.ticket_repo.get_ticket_historial(id_ticket)
    #     return [InformacionTicket.model_validate(h) for h in registros]
    
    # def listar_ticket_paginado(
    #     self,
    #     estado = None,
    #     prioridad = None,
    #     activo = None,
    #     titulo = None,
    #     page: int = 1,
    #     size: int = 10
    # ):
    #     skip = (page - 1) * size
    #     tickets, total = self.ticket_repo.listar_ticket_filtro(
    #         estado, 
    #         prioridad, 
    #         activo, 
    #         titulo, 
    #         skip, 
    #         size)
        
    #     return {
    #         "items": [InformacionTicket.model_validate(t) for t in tickets],
    #         "total": total,
    #         "page": page,
    #         "size": size,
    #         "pages": ceil(total / size)
    #     }
            
        