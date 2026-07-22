from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITMO: str
    JWT_TIEMPO_EXPIRACION: int
    NOMBRE_PROYECTO: str = "TicketFlow"
    AMBIENTE: str = "DESARROLLO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


configuracion = Configuracion()