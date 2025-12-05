from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host:str = Field(default='localhost', alias='HOST')
    port:int = Field(default=8001, alias='PORT')
    
    # Format: "amount/period" (e.g., "5/minute", "10/second", "100/hour")
    default_rate_limit: str = Field(default="1/second", alias="RATE_LIMIT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
