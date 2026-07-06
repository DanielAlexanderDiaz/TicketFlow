from typing import Optional
from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Session, select, delete
from app.core.seguridad import RolUsuario
from app.models.usuario import Usuario

class UsuarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def get_usuario_by_id(self, id_usuario: int) -> Usuario | None:
        return self.db.get(Usuario, id_usuario)

    def get_usuario_by_email(self, email: EmailStr) -> Usuario | None:
        query = select(Usuario).where(Usuario.email == email)
        return self.db.exec(query).first()
    
    def listar_usuarios(self) -> list[Usuario] | None:
        query = select(Usuario)
        return self.db.exec(query).all()
    
    def crear_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def eliminar_usuario(self, usuario: Usuario) -> None:
        self.db.exec(delete(Usuario).where(Usuario.id == usuario.id))
        self.db.delete(usuario)
        self.db.commit()
        
    def buscar_usuario(self,
                       buscar_email: Optional[str],
                       buscar_nombre: Optional[str],
                       rol: Optional[RolUsuario],
                       activo: Optional[bool],
                       orden: str,
                       direccion: str,
                       limit: int,
                       offset: int,
                       ) -> tuple[int, list[Usuario]]:
        stmt = select(Usuario)
        
        # Busqueda - Coincidencia parcial
        if buscar_email is not None:
            stmt = stmt.where(Usuario.email.ilike(f"%{buscar_email}%"))
        if buscar_nombre is not None:
            stmt = stmt.where(Usuario.nombre_usuario.ilike(f"%{buscar_nombre}%"))
            
        # Filtros - Coincidencia exacta
        if rol is not None:
            stmt = stmt.where(Usuario.rol == rol)
        if activo is not None:
            stmt = stmt.where(Usuario.activo == activo)
        
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if total == 0:
            return 0, []    
            
        # Ordenar
        columnas_orden = {
            "id": Usuario.id,
            "email": Usuario.email,
            "nombre_usuario": Usuario.nombre_usuario,
            "activo": Usuario.activo,
        }
        
        orden_col = columnas_orden.get(orden, Usuario.id)
        stmt = stmt.order_by(orden_col.asc() if direccion == "asc" else orden_col.desc())
        
        items = self.db.exec(stmt.limit(limit).offset(offset)).all()
        return total, items
        
        