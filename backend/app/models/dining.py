import uuid
from datetime import date, datetime, time
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.enums import MealPeriod
from models.base import Base

class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()")
    )
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # Relationships
    schedules: Mapped[list["LocationSchedule"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )
    dishes: Mapped[list["Dish"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )
    daily_menu_dishes: Mapped[list["DailyMenuDish"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )


class LocationSchedule(Base):
    __tablename__ = "location_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()")
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # Relationships
    location: Mapped["Location"] = relationship(back_populates="schedules")


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()")
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ingredients: Mapped[str | None] = mapped_column(String(500), nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    portion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("name", "location_id", name="dishes_name_location_unique"),
    )

    # Relationships
    location: Mapped["Location"] = relationship(back_populates="dishes")
    servings: Mapped[list["DailyMenuDish"]] = relationship(
        back_populates="dish", cascade="all, delete-orphan"
    )


class DailyMenuDish(Base):
    __tablename__ = "daily_menu_dishes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()")
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False
    )
    dish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False
    )
    served_date: Mapped[date] = mapped_column(Date, nullable=False)
    period: Mapped[MealPeriod] = mapped_column(
        SQLEnum(
            MealPeriod,
            name="meal_period",
            values_callable=lambda obj: [e.value for e in obj],
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
    )
    station: Mapped[str] = mapped_column(String(255), server_default="General", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "location_id", "dish_id", "served_date", "period", "station",
            name="unique_daily_serving"
        ),
        Index("idx_daily_menu_lookup", "served_date", "location_id", "period"),
    )

    # Relationships
    location: Mapped["Location"] = relationship(back_populates="daily_menu_dishes")
    dish: Mapped["Dish"] = relationship(back_populates="servings")
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="daily_menu_dish", cascade="all, delete-orphan"
    )


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()")
    )
    daily_menu_dishes_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_menu_dishes.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 10", name="ratings_score_check"),
        UniqueConstraint("daily_menu_dishes_id", "client_id", name="unique_user_daily_rating"),
        Index("idx_ratings_menu_dish", "daily_menu_dishes_id"),
    )

    # Relationships
    daily_menu_dish: Mapped["DailyMenuDish"] = relationship(back_populates="ratings")