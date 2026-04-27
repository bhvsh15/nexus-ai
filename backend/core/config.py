#Imports
from pydantic_settings import BaseSettings, SettingsConfigDict

# This file defines the configuration settings for the Nexus AI application using Pydantic's BaseSettings.
class Settings(BaseSettings):
    app_name: str = "Nexus AI"
    debug: bool = False
    database_url: str = "sqlite:///./nexus_ai.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "gemma4:e2b"

    model_config = SettingsConfigDict(env_file=".env") 

# Create an instance of the Settings class to be used throughout the application.
settings = Settings()

