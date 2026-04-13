from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey,String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

if TYPE_CHECKING:
      from backend.app.db.models.document import Document



class Chunk(Base):
      """Text/Image chunk for retrieval"""
      __tablename__ = "chunks"

      id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
      document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
      chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
      content: Mapped[str] = mapped_column(Text, nullable=False)
      chunk_type: Mapped[str] = mapped_column(String(20), default="text")  # text or image
      metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string for extra info
      created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

      document: Mapped["Document"] = relationship("Document", back_populates="chunks")