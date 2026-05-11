from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.models.ticket import ActualizarTicket, CrearTicket, InfoTicket
from app.services.ticket_services import TicketService


router = APIRouter(prefix="/ticket", tags=["ticket"])

@router.get("/", response_model=InfoTicket)
def info_ticket(id_ticket: int, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).ticket_by_id(id_ticket)

@router.post("/", response_model=CrearTicket, status_code=status.HTTP_201_CREATED)
def crear_ticket(id_usuario: int, payload: CrearTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).crear_ticket(id_usuario, payload)

@router.patch("/{id_ticket}", response_model=InfoTicket)
def actualizar_ticket(id_ticket: int, payload: ActualizarTicket, db: DBSession, usuario: UsuarioActual):
    return TicketService(db).actualizar_ticket(id_ticket, payload)