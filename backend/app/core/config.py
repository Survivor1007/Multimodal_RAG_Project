from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
      model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
      )

      #General 
      PROJECT_NAME: str = Field(default="Multimodal Hybrid RAG System")
      ENVIRONMENT: str = Field(default="development")
      DEBUG: bool = Field(default=True)
      API_V1_STR: str = Field(default="/api/v1")

      # Database
      DATABASE_URL: str

      # Logging
      LOG_LEVEL: str = Field(default="INFO")

      # ML - will be extended in Phase 2
      EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
      CLIP_MODEL: str = Field(default="openai/clip-vit-base-patch32")
      FAISS_INDEX_PATH: str = Field(default="data/indexes/faiss.index")
      BM25_INDEX_PATH: str = Field(default="data/indexes/bm25_index.pkl")


settings = Settings()