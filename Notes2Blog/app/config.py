from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"

    USE_OPENAI_VISION: bool = True
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_VISION_MODEL: str = "gpt-4o-mini"
    OPENAI_TEXT_MODEL: str = "gpt-4o-mini"

    REQUIRE_H1: bool = True
    REQUIRE_SECTIONS: bool = True
    
    # Image compression settings to reduce token usage
    MAX_IMAGE_SIZE: tuple = (1024, 1024)  # Max width/height in pixels
    IMAGE_QUALITY: int = 85  # JPEG quality (1-95, lower = smaller file)
    
    # DSPy optimization settings
    LM_TEMPERATURE: float = 0.1  # Lower temperature for more consistent outputs
    MAX_TOKENS: int = 2000  # Limit output length

    class Config:
        env_file = ".env"

settings = Settings()


