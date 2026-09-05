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
      API_V2_STR: str = Field(default="/api/v2")

      # Database
      DATABASE_URL: str

      # Logging
      LOG_LEVEL: str = Field(default="INFO")

      # ML - Model settings & Fine-tuned weights support
      EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
      EMBEDDING_MODEL_PATH: str | None = Field(default=None, description="Path to fine-tuned sentence-transformer model directory")
      CLIP_MODEL: str = Field(default="openai/clip-vit-base-patch32")
      RERANKER_MODEL: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
      RERANKER_MODEL_PATH: str | None = Field(default=None, description="Path to fine-tuned cross-encoder model directory")
      FAISS_INDEX_PATH: str = Field(default="data/indexes/faiss.index")
      FAISS_IMAGE_INDEX_PATH: str = Field(default="data/indexes/faiss_image.index")
      BM25_INDEX_PATH: str = Field(default="data/indexes/bm25_index.pkl")

      # Groq LLM
      GROQ_API_KEY: str | None = Field(default=None, description="Groq API Key")
      GROQ_MODEL: str = Field(default="llama-3.1-8b-instant", description="Groq model")

      # Tavily Web Search
      TAVILY_API_KEY: str | None = Field(default=None, description="Tavily API Key")
      WEB_SEARCH_THRESHOLD: float = Field(default=0.65, description="Confidence threshold to trigger web search")
      TAVILY_MAX_RESULTS: int = Field(default=5, description="Max web results")


settings = Settings()