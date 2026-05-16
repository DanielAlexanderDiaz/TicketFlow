from fastapi import APIRouter, Depends, status
from app.api.dependencias import DBSession, UsuarioActual, requiere_admin, puede_gestionar_ticket
from app.schemas.ticket import InfoTicket, ActualizarTicket, CrearTicket, HistorialTicket
from app.services.ticket_services import TicketService

router = APIRouter(prefix="/ticket", tags=["ticket"])

@router.get("/", response_model=InfoTicket)
def informacion_del_ticket(id_ticket: int, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_id(id_ticket, usuario.id)

@router.get("/listar", response_model=list[InfoTicket])
def listar_tickets_usuario(db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_usuario(usuario.id)

@router.get("/listar_todos", response_model=list[InfoTicket], dependencies=[Depends(requiere_admin)])
def listar_todos_los_tickets(db: DBSession):
    return TicketService(db).listar_tickets()

@router.get("/{id_ticket}/historial", response_model=list[HistorialTicket], dependencies=[Depends(requiere_admin)])
def obtener_historial(id_ticket: int, db: DBSession):
    return TicketService(db).obtener_historial(id_ticket)

@router.post("/", response_model=InfoTicket, status_code=status.HTTP_201_CREATED, dependencies=[Depends(puede_gestionar_ticket)])
def crear_ticket(payload: CrearTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).crear_ticket(usuario.id, payload)

@router.patch("/{id_ticket}", response_model=InfoTicket, dependencies=[Depends(puede_gestionar_ticket)])
def actualizar_ticket(id_ticket: int, payload: ActualizarTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).actualizar_ticket(id_ticket, payload, usuario.id)