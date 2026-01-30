import os


class Settings:
    SERVICE_NAME = os.getenv("SERVICE_NAME", "event-driven-service")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
