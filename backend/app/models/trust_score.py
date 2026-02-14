import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.types import PortableJSON


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    grade: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # gold | silver | bronze | fail
    certification: Mapped[str] = mapped_column(String(50), nullable=False)
    is_certifiable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    breakdown: Mapped[dict] = mapped_column(PortableJSON, nullable=False)
    improvement_potential: Mapped[dict | None] = mapped_column(
        PortableJSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="trust_scores")  # noqa: F821
    connection: Mapped["Connection"] = relationship(  # noqa: F821
        back_populates="trust_scores"
    )
    anomalies: Mapped[list["Anomaly"]] = relationship(  # noqa: F821
        back_populates="trust_score", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(  # noqa: F821
        back_populates="trust_score", cascade="all, delete-orphan"
    )
