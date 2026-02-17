from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(10), unique=True, nullable=False)
    seller_id = Column(String(50), nullable=False)  # In a real system, would be Foreign Key
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    clicks = relationship("Click", back_populates="link")
    monthly_stats = relationship("MonthlyStat", back_populates="link")

    def __repr__(self):
        return f"<Link(id={self.id}, short_code={self.short_code})>"


class Click(Base):
    __tablename__ = 'clicks'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id'), nullable=False)
    clicked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_valid = Column(Boolean, default=False)  # Determined by fraud validation
    rewarded = Column(Boolean, default=False)  # Whether the reward was processed

    # Relationships
    link = relationship("Link", back_populates="clicks")

    def __repr__(self):
        return f"<Click(id={self.id}, link_id={self.link_id}, valid={self.is_valid})>"


class MonthlyStat(Base):
    __tablename__ = 'monthly_stats'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id'), nullable=False)
    year_month = Column(String(7), nullable=False)  # Format: YYYY-MM
    clicks = Column(Integer, default=0)
    valid_clicks = Column(Integer, default=0)
    rewards_earned = Column(Float, default=0.0)

    # Relationships
    link = relationship("Link", back_populates="monthly_stats")

    def __repr__(self):
        return f"<MonthlyStat(link_id={self.link_id}, year_month={self.year_month})>"