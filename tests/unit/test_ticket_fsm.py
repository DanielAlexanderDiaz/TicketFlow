import pytest
from app.core.ticket_fsm import TicketFSM
from app.models.ticket import EstadoTicket


class TestTicketFSM:
    def test_transicion_valida_pendiente_a_en_progreso(self):
        fsm = TicketFSM(EstadoTicket.PENDIENTE)
        nuevo_estado = fsm.transicionar(EstadoTicket.EN_PROGRESO)
        assert nuevo_estado == EstadoTicket.EN_PROGRESO
        assert fsm.estado_actual == EstadoTicket.EN_PROGRESO

    def test_transicion_valida_en_progreso_a_finalizado(self):
        fsm = TicketFSM(EstadoTicket.EN_PROGRESO)
        assert fsm.transicionar(EstadoTicket.FINALIZADO) == EstadoTicket.FINALIZADO

    def test_transicion_invalida_lanza_value_error(self):
        fsm = TicketFSM(EstadoTicket.PENDIENTE)
        with pytest.raises(ValueError, match="No se puede transicionar"):
            fsm.transicionar(EstadoTicket.FINALIZADO)

    def test_finalizado_es_estado_terminal(self):
        fsm = TicketFSM(EstadoTicket.FINALIZADO)
        assert fsm.puede_transicionar(EstadoTicket.PENDIENTE) is False
        assert fsm.puede_transicionar(EstadoTicket.EN_PROGRESO) is False

    # parametrize = una sola función cubre toda la matriz de transiciones
    @pytest.mark.parametrize("origen,destino,esperado", [
        (EstadoTicket.PENDIENTE, EstadoTicket.EN_PROGRESO, True),
        (EstadoTicket.PENDIENTE, EstadoTicket.FINALIZADO, False),
        (EstadoTicket.EN_PROGRESO, EstadoTicket.FINALIZADO, True),
        (EstadoTicket.EN_PROGRESO, EstadoTicket.PENDIENTE, False),
        (EstadoTicket.FINALIZADO, EstadoTicket.EN_PROGRESO, False),
    ])
    def test_matriz_transiciones(self, origen, destino, esperado):
        fsm = TicketFSM(origen)
        assert fsm.puede_transicionar(destino) is esperado