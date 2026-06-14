"""
SplunkSentinel Configuration — Environment-based settings management.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    SPLUNK_HOST: str = "localhost"
    SPLUNK_PORT: int = 8089
    SPLUNK_TOKEN: str = ""
    SPLUNK_MCP_ENDPOINT: str = "http://localhost:8088/mcp"
    FOUNDATION_SEC_ENDPOINT: str = "http://localhost:8089/services/ML/models/foundation-sec"
    CISCO_DTSM_ENDPOINT: str = "http://localhost:8089/services/ML/models/cisco-dtsm"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173
    LOG_LEVEL: str = "INFO"
    DEMO_MODE: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
