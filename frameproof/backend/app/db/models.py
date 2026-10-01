"""FrameProof SQLAlchemy ORM Models.

Purpose: Persistent schema for forensic cases, seized devices, and evidence images.
Inputs: Relational database schemas.
Outputs: Mapped ORM classes.
Status: Implemented
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CaseModel(Base):
    """Forensic investigation case record."""

    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    investigator_name: Mapped[str] = mapped_column(String(128), nullable=False)
    agency: Mapped[str] = mapped_column(String(128), default="Forensic Science Laboratory")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidence_images: Mapped[list["EvidenceImageModel"]] = relationship(
        "EvidenceImageModel", back_populates="case", cascade="all, delete-orphan"
    )


class EvidenceImageModel(Base):
    """Acquired bit-stream disk image attached to a case."""

    __tablename__ = "evidence_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    format: Mapped[str] = mapped_column(String(32), default="RAW_DD")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["CaseModel"] = relationship("CaseModel", back_populates="evidence_images")
