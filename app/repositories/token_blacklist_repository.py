from datetime import datetime
from sqlmodel import Session, select
from app.models.token_black_list import TokenBlackList


class TokenBlackListRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def agregar(self, jti: str, expira_en: datetime) -> TokenBlackList:
        entrada = TokenBlackList(jti=jti, expira_en=expira_en)
        self.db.add(entrada)
        self.db.commit()
        return entrada
    
    def esta_en_blacklist(self, jti: str) -> bool:
        resultado = self.db.exec(select(TokenBlackList).where(TokenBlackList.jti == jti)).first()
        return resultado is not None
    
    def limpiar_expirados(self) -> int:
        ahora = datetime.now()
        expirados = self.db.exec(select(TokenBlackList).where(TokenBlackList.expira_en < ahora)).all()
        for registros in expirados:
            self.db.delete(registros)
        self.db.commit()
        return len(expirados)