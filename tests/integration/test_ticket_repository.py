import pytest
from app.models.ticket import Ticket, PrioridadTicket
from app.repositories.ticket_repository import TicketRepositorio


@pytest.fixture
def repo(session):
    return TicketRepositorio(session)


def _crear_ticket(session, **kwargs):
    defaults = dict(
        titulo="ticket",
        descripcion="desc",
        id_usuario_creador=1,
        prioridad=PrioridadTicket.BAJA,
    )
    defaults.update(kwargs)
    ticket = Ticket(**defaults)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def _args_base(**overrides):
    base = dict(
        ids_permitidos=None, buscar_titulo=None, buscar_descripcion=None,
        id_ticket=None, prioridad=None, estado=None, asignado=None,
        fecha_desde=None, fecha_hasta=None, orden="id", direccion="asc",
        limit=10, offset=0,
    )
    base.update(overrides)
    return base


class TestBuscarTicketABAC:
    def test_ids_permitidos_none_es_superadmin_ve_todo(self, session, repo):
        _crear_ticket(session, titulo="A", id_usuario_creador=1)
        _crear_ticket(session, titulo="B", id_usuario_creador=2)

        total, items = repo.buscar_ticket(**_args_base(ids_permitidos=None))

        assert total == 2

    def test_ids_permitidos_vacio_no_devuelve_nada(self, session, repo):
        _crear_ticket(session, titulo="A", id_usuario_creador=1)

        total, items = repo.buscar_ticket(**_args_base(ids_permitidos=set()))

        assert total == 0
        assert items == []

    def test_ids_permitidos_filtra_solo_los_propios(self, session, repo):
        propio = _crear_ticket(session, titulo="Mio", id_usuario_creador=1)
        _crear_ticket(session, titulo="Ajeno", id_usuario_creador=2)

        total, items = repo.buscar_ticket(**_args_base(ids_permitidos={propio.id}))

        assert total == 1
        assert items[0].titulo == "Mio"


class TestBusquedaYOrdenamiento:
    def test_busqueda_parcial_ilike_por_titulo(self, session, repo):
        _crear_ticket(session, titulo="Bug en login")
        _crear_ticket(session, titulo="Nueva feature")

        total, items = repo.buscar_ticket(**_args_base(buscar_titulo="bug"))

        assert total == 1
        assert "Bug" in items[0].titulo

    def test_paginacion_respeta_limit_y_offset(self, session, repo):
        for i in range(5):
            _crear_ticket(session, titulo=f"Ticket {i}")

        total, items = repo.buscar_ticket(**_args_base(limit=2, offset=2))

        # el total ignora la paginación, items sí la respeta
        assert total == 5
        assert len(items) == 2
        assert items[0].titulo == "Ticket 2"