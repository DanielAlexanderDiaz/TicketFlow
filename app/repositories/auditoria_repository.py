from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlmodel import Session, select
from app.models.auditoria import Auditoria


class AuditoriaRepositorio:
    def __init__(self, db: Session):
        self.db = db
    
    def crear_audtoria(self, auditoria: Auditoria) -> Auditoria:
        self.db.add(auditoria)
        self.db.commit()
        self.db.refresh(auditoria)
        return auditoria
    
    def get_ticket_historial(self, id_ticket: int) -> list[Auditoria]:
        query = select(Auditoria).where(Auditoria.id_entidad == id_ticket)
        return self.db.exec(query).all()
    
    def buscar_auditoria(self,
                        entidad: Optional[str],
                        id_entidad: Optional[int],
                        id_usuario: Optional[int],
                        campo_cambiado: Optional[str],
                        accion: Optional[str],
                        fecha_desde: Optional[datetime],
                        fecha_hasta: Optional[datetime],
                        orden: str,
                        direccion: str,
                        limit: int,
                        offset: int,
                        ) -> tuple[int, list[Auditoria]]:
        stmt = select(Auditoria)
        
        # Busqueda - Coincidencia parcial
        if campo_cambiado is not None:
            stmt = stmt.where(Auditoria.campo_cambiado.ilike(f"%{campo_cambiado}%"))
        if accion is not None:
            stmt = stmt.where(Auditoria.accion.ilike(f"%{accion}%"))
            
        # Filtros - Coincidencia exacta
        if entidad is not None:
            stmt = stmt.where(Auditoria.entidad == entidad)
        if id_entidad is not None:
            stmt = stmt.where(Auditoria.id_entidad == id_entidad)
        if id_usuario is not None:
            stmt = stmt.where(Auditoria.id_usuario == id_usuario)
        if fecha_desde is not None:
            stmt = stmt.where(Auditoria.fecha_cambio >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(Auditoria.fecha_cambio <= fecha_hasta)
        
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if total == 0:
            return 0, []
        
        # Ordenamiento
        columna_orden = {
            "id": Auditoria.id,
            "id_entidad": Auditoria.id_entidad,
            "id_usuario": Auditoria.id_usuario,
            "fecha_cambio": Auditoria.fecha_cambio
        }
        
        orden_col = columna_orden.get(orden, Auditoria.id)
        stmt = stmt.order_by(orden_col.asc() if direccion == "asc" else orden_col.desc())
        
        items = self.db.exec(stmt.limit(limit).offset(offset)).all()
        return total, items