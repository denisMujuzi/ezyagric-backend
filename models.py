# models.py
from sqlalchemy import String, Integer, Date, Text, ForeignKey, Enum, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from dependencies import nairobi_tz
from datetime import datetime


class Base(DeclarativeBase):
    pass


class StatusType(PyEnum):
    COMPLETED = "COMPLETED"
    UPCOMING = "UPCOMING"
    OVERDUE = "OVERDUE"


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phoneNumber: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    gender: Mapped[str] = mapped_column(String(255), nullable=True)
    hashedPassword: Mapped[str] = mapped_column(String(255), nullable=False)
    createdAt: Mapped[Date] = mapped_column(Date, nullable=False, default=lambda: datetime.now(nairobi_tz))


    farms: Mapped[list["Farm"]] = relationship(
        back_populates="farmer", cascade="all, delete-orphan"
    )


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmerId: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sizeAcres: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    farmer: Mapped[Farmer] = relationship(back_populates="farms")
    season_plans: Mapped[list["SeasonPlan"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )


class SeasonPlan(Base):
    __tablename__ = "season_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmId: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id"), nullable=False)
    cropName: Mapped[str] = mapped_column(String(120), nullable=False)
    seasonName: Mapped[str] = mapped_column(String(120), nullable=False)

    farm: Mapped[Farm] = relationship(back_populates="season_plans")
    planned_activities: Mapped[list["PlannedActivity"]] = relationship(
        back_populates="season_plan", cascade="all, delete-orphan"
    )
    actual_activities: Mapped[list["ActualActivity"]] = relationship(
        back_populates="season_plan", cascade="all, delete-orphan"
    )


class PlannedActivity(Base):
    __tablename__ = "planned_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seasonPlanId: Mapped[int] = mapped_column(Integer, ForeignKey("season_plans.id"), nullable=False)
    activityType: Mapped[str] = mapped_column(String(50), nullable=False)
    targetDate: Mapped[Date] = mapped_column(Date, nullable=False)
    estimatedCostUgx: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[StatusType] = mapped_column(Enum(StatusType), nullable=False)

    season_plan: Mapped[SeasonPlan] = relationship(back_populates="planned_activities")
    actual_activities: Mapped[list["ActualActivity"]] = relationship(
        back_populates="planned_activity"
    )


class ActualActivity(Base):
    __tablename__ = "actual_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seasonPlanId: Mapped[int] = mapped_column(Integer, ForeignKey("season_plans.id"), nullable=False)
    activityType: Mapped[str] = mapped_column(String(50), nullable=False)
    actualDate: Mapped[Date] = mapped_column(Date, nullable=False)
    actualCostUgx: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    plannedActivityId: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("planned_activities.id"), nullable=True
    )

    season_plan: Mapped[SeasonPlan] = relationship(back_populates="actual_activities")
    planned_activity: Mapped[PlannedActivity | None] = relationship(back_populates="actual_activities")
