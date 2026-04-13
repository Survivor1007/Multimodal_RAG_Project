from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

if TYPE_CHECKING:
      from backend.app.db.models.chunk import Chunk



class Document(Base):
      """Document metadata"""
      __tablename__ = "documents"

      id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
      title: Mapped[str] = mapped_column(String(500), nullable=False)
      file_name: Mapped[str] = mapped_column(String(255), nullable=False)
      file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, jpg, etc.
      content_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
      user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
      created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

      # Relationships
      chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")