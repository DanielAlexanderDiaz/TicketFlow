from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TokenBlackList(SQLModel, table=True):
    __tablename__ = "token_black_list"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(unique=True, index=True)
    expira_en: datetime
    creado_en: datetime = Field(default_factory=datetime.now)