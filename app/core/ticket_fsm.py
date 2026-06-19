from app.models.ticket import EstadoTicket, TRANSICIONES_PERMITIDAS

class TicketFSM:
    def __init__(self, estado_actual: EstadoTicket):
        self.estado_actual = estado_actual
        
    def puede_transicionar(self, nuevo_estado: EstadoTicket) -> bool:
        transiciones_validas = TRANSICIONES_PERMITIDAS.get(self.estado_actual, [])
        return nuevo_estado in transiciones_validas
    
    def transicionar(self, nuevo_estado: EstadoTicket) -> EstadoTicket:
        if not self.puede_transicionar(nuevo_estado):
            raise ValueError(f"No se puede transicionar del estado {self.estado_actual} al estado {nuevo_estado}")
        
        self.estado_actual = nuevo_estado
        return self.estado_actual
    