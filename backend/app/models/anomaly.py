import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.types import PortableJSON


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    trust_score_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trust_scores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # consistency | outlier | duplicate
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # critical | medium | low
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    financial_impact_eur: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    details: Mapped[dict | None] = mapped_column(PortableJSON, nullable=True)
    remediation_proposal: Mapped[dict | None] = mapped_column(
        PortableJSON, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="open"
    )  # open | in_progress | resolved
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    trust_score: Mapped["TrustScore"] = relationship(  # noqa: F821
        back_populates="anomalies"
    )
