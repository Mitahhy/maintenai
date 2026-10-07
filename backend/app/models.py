from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def now():
    return datetime.now(timezone.utc)


class Site(Base):
    __tablename__ = "sites"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    designation: Mapped[str] = mapped_column(String(200))
    criticality: Mapped[str] = mapped_column(String(20), default="standard")
    site_id: Mapped[int | None] = mapped_column(ForeignKey("sites.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"))
    counter_hours: Mapped[float | None] = mapped_column(Float)
    warranty_until: Mapped[date | None] = mapped_column(Date)


class WorkOrder(Base):
    __tablename__ = "work_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str | None] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    wo_type: Mapped[str] = mapped_column(String(20))  # corrective | preventive | predictive
    status: Mapped[str] = mapped_column(String(20), default="to_plan")
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))
    assignee: Mapped[str | None] = mapped_column(String(120))
    hours_spent: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Part(Base):
    __tablename__ = "parts"
    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(60), unique=True)
    label: Mapped[str] = mapped_column(String(200))
    stock_qty: Mapped[int] = mapped_column(default=0)
    min_qty: Mapped[int] = mapped_column(default=0)


class PredictiveAlert(Base):
    __tablename__ = "predictive_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))
    signal: Mapped[str] = mapped_column(String(200))
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="new")  # new | accepted | rejected
    work_order_id: Mapped[int | None] = mapped_column(ForeignKey("work_orders.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
