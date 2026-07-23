from typing import Iterator
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import configuracion
from sqlalchemy import event


motor = create_engine(
    configuracion.DATABASE_URL,
    echo=True,
    connect_args=(
        {"check_same_thread": False}
        if "sqlite" in configuracion.DATABASE_URL
        else {}
    ),
)

@event.listens_for(motor, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in configuracion.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close() 
    
def init_db() -> None:
    if configuracion.AMBIENTE == "DESARROLLO":
        SQLModel.metadata.create_all(motor)

def get_session() -> Iterator[Session]:
    with Session(motor) as session:
        yield session