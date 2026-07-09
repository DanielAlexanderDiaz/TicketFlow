from datetime import date
from typing import Optional
from sqlalchemy import func
from sqlmodel import Session, select, delete
from app.models.comentario import Comentario

class ComentarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_comentario_by_id(self, id_comentario: int) -> Comentario | None:
        return self.db.get(Comentario, id_comentario)
    
    def get_comentario_by_ticket(self, id_ticket: int) -> list[Comentario]:
        query = select(Comentario).where(Comentario.id_ticket == id_ticket)
        return self.db.exec(query).all()
    
    def get_comentario_by_usuario(self, id_usuario: int) -> list[Comentario]:
        query = select(Comentario).where(Comentario.id_usuario == id_usuario)
        return self.db.exec(query).all()
    
    def crear_comentario(self, comentario: Comentario) -> Comentario:
        self.db.add(comentario)
        self.db.commit()
        self.db.refresh(comentario)
        return comentario
    
    def actualizar_comentario(self, comentario: Comentario) -> Comentario:
        self.db.commit()
        self.db.refresh(comentario)
        return comentario
    
    def eliminar_comentario(self, id_comentario: int) -> None:
        self.db.exec(delete(Comentario).where(Comentario.id == id_comentario))
        self.db.commit()

    def ultimo_comentario(self, id_ticket: int) -> Comentario | None:
        query = select(Comentario).where(Comentario.id_ticket == id_ticket).order_by(Comentario.id.desc()).limit(1)
        return self.db.exec(query).first()
    
    def buscar_comentario(self,
                        ids_permitidos: Optional[set[int]],
                        id_ticket: Optional[int],
                        id_usuario: Optional[int],
                        comentario: Optional[str],
                        fecha_creacion: Optional[date],
                        fecha_actualizacion: Optional[date],
                        orden: str,
                        direccion: str,
                        limit: int,
                        offset: int,
                        ) -> tuple[int, list[Comentario]]:
        stmt = select(Comentario)
        
        if ids_permitidos is not None:
            if not ids_permitidos:
                return 0, []
            stmt = stmt.where(Comentario.id_ticket.in_(ids_permitidos))
            
        # Filtros - Coincidencia exacta
        if id_ticket is not None:
            stmt = stmt.where(Comentario.id_ticket == id_ticket)
        if id_usuario is not None:
            stmt = stmt.where(Comentario.id_usuario == id_usuario)
        if comentario is not None:
            stmt = stmt.where(Comentario.comentario.ilike(f"%{comentario}%"))
        if fecha_creacion is not None:
            stmt = stmt.where(Comentario.fecha_creacion == fecha_creacion)
        if fecha_actualizacion is not None:
            stmt = stmt.where(Comentario.fecha_actualizacion == fecha_actualizacion)
        
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if total == 0:
            return 0, []
        
        # Ordenar
        columnas_orden = {
            "id": Comentario.id,
            "id_ticket": Comentario.id_ticket,
            "id_usuario": Comentario.id_usuario,
            "fecha_creacion": Comentario.fecha_creacion,
            "fecha_actualizacion": Comentario.fecha_actualizacion,
        }
        
        orden_col = columnas_orden.get(orden, Comentario.id)
        stmt = stmt.order_by(orden_col.asc() if direccion == "asc" else orden_col.desc())
        
        items = self.db.exec(stmt.offset(offset).limit(limit)).all()
        return total, items