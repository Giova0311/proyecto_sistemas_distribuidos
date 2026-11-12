from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "mysql-primary"
    db_port: int = 3306
    db_name: str = "pedidos"
    db_user: str = "pedidos_app"
    db_password: str
    node_id: str = "backend-local"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
