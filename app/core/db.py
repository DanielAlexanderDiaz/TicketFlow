from typing import Iterator
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import configuracion

motor = create_engine(
    configuracion.DATABASE_URL,
    echo=True,
    connect_args=(
        {"check_same_thread": False}
        if 'sqlite' in configuracion.DATABASE_URL
        else {}
    ),
)

def init_db() -> None:
    SQLModel.metadata.create_all(motor)
    
    
def get_session() -> Iterator[Session]:
    with Session(motor) as session:
        yield session