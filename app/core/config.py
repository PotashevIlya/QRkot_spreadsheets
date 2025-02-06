from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title: str = 'Сервси пожертвований для котиков'
    database_url: str = 'sqlite+aiosqlite:///./catcharityfund.db'
    secret: str = 'secret'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
