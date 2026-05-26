from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from app.api.dependencias import DBSession, UsuarioActual, requiere_admin, puede_gestionar_ticket
from app.models.ticket import EstadoTicket, PrioridadTicket
from app.schemas.ticket import ActualizarEstadoTicket, ActualizarTickekActivo, InfoTicket, ActualizarTicket, CrearTicket, HistorialTicket, PaginacionTicket
from app.services.ticket_estado_services import TicketEstadoServices
from app.services.ticket_services import TicketService

router = APIRouter(prefix="/ticket", tags=["ticket"])

@router.get("/listar", response_model=list[InfoTicket])
def listar_tickets_usuario(db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_usuario(usuario.id)

@router.get("/listar_todos", response_model=list[InfoTicket], dependencies=[Depends(requiere_admin)])
def listar_todos_los_tickets(db: DBSession):
    return TicketService(db).listar_tickets()

@router.get("/listar_paginado", response_model=PaginacionTicket, dependencies=[Depends(requiere_admin)])
def listar_ticket_paginado(
    db: DBSession,
    estado: Optional[EstadoTicket] = Query(None, description="Filtrar por estado"),
    prioridad: Optional[PrioridadTicket] = Query(None, description="Filtrar por prioridad"),
    activo: Optional[bool] = Query(None, description="Filtrar por activo/inactivo"),
    titulo: Optional[str] = Query(None, max_length=100, description="Filtrar por titulo (Parcial)"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Número de elementos por página"),
    ):
    return TicketService(db).listar_ticket_paginado(estado, prioridad, activo, titulo, page, size)

@router.post("/", response_model=InfoTicket, status_code=status.HTTP_201_CREATED, dependencies=[Depends(puede_gestionar_ticket)])
def crear_ticket(payload: CrearTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).crear_ticket(usuario.id, payload)

@router.get("/", response_model=InfoTicket)
def informacion_del_ticket(id_ticket: int, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_id(id_ticket, usuario.id)

@router.patch("/{id_ticket}", response_model=InfoTicket, dependencies=[Depends(puede_gestionar_ticket)])
def actualizar_ticket(id_ticket: int, payload: ActualizarTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).actualizar_ticket(id_ticket, payload, usuario.id)

@router.patch("/{id_ticket}/vigencia", response_model=InfoTicket, dependencies=[Depends(puede_gestionar_ticket)])
def actualizar_ticket_activo(id_ticket: int, payload: ActualizarTickekActivo, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).actualizar_ticket_activo(id_ticket, usuario.id, payload)

@router.patch("/{id_ticket}/imagen", response_model=InfoTicket, dependencies=[Depends(puede_gestionar_ticket)])
def actualizar_imagen_ticket(db: DBSession, usuario: UsuarioActual,id_ticket: int, img: Optional[UploadFile] = File(None)):
    payload = ActualizarTicket(imagen_url=img)
    return TicketService(db).actualizar_ticket(id_ticket, payload, usuario.id)

@router.patch("/{id_ticket}/estado", response_model=InfoTicket, dependencies=[Depends(puede_gestionar_ticket)])
def actualizar_cambiar_estado(db: DBSession, id_ticket: int, new_estado: ActualizarEstadoTicket, usuario: UsuarioActual):
    return TicketEstadoServices(db).cambiar_estado_ticket(id_ticket, new_estado)

@router.get("/{id_ticket}/historial", response_model=list[HistorialTicket], dependencies=[Depends(requiere_admin)])
def obtener_historial(id_ticket: int, db: DBSession):
    try:   
        return TicketService(db).obtener_historial(id_ticket)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))