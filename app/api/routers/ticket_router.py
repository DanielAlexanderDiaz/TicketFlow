from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.models.ticket import ActualizarTicket, CrearTicket, HistorialTicket, InfoTicket
from app.services.ticket_services import TicketService


router = APIRouter(prefix="/ticket", tags=["ticket"])

@router.get("/", response_model=InfoTicket)
def info_ticket(id_ticket: int, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_id(id_ticket)

@router.get("/listar", response_model=list[InfoTicket])
def listar_tickets(db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_usuario(usuario.id)

@router.get("/listar_todos", response_model=list[InfoTicket])
def listar_tickets(db: DBSession, usuario: UsuarioActual):
    return TicketService(db).listar_tickets()

@router.get("/{id_ticket}/historial", response_model=list[HistorialTicket])
def obtener_historial(id_ticket: int, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).obtener_historial(id_ticket)

@router.post("/", response_model=CrearTicket, status_code=status.HTTP_201_CREATED)
def crear_ticket(payload: CrearTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).crear_ticket(usuario.id, payload)

@router.patch("/{id_ticket}", response_model=InfoTicket)
def actualizar_ticket(id_ticket: int, payload: ActualizarTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).actualizar_ticket(id_ticket, payload, usuario.id)