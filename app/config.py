import os

class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass

class Settings:
    def __init__(self) -> None:
        self.SERVICE_NAME = os.getenv("SERVICE_NAME", "event-driven-service")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

        self.validate()
    
    def validate(self) -> None:
        allowed_envs = {"dev", "staging", "prod"}
        if self.ENVIRONMENT not in allowed_envs:
            raise ConfigError(
                f"ENVIRONMENT must be one of {sorted(allowed_envs)}, got '{self.ENVIRONMENT}'"
            )
        
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.LOG_LEVEL not in allowed_levels:
            raise ConfigError(
                f"LOG_LEVEL must be one of {sorted(allowed_levels)}, got '{self.LOG_LEVEL}'"
            )


settings = Settings()
