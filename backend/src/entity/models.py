import enum
from datetime import date
from typing import List

from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    func,
    Enum,
    Integer,
    Float,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the FastAPI application."""

    pass


class TimeStampMixin:
    """Mixin class providing timestamp information (created_at, updated_at) for SQLAlchemy models."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True
    )
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )


class Picture(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'pictures' table in the database."""

    __tablename__ = "pictures"
    find_plate: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String, nullable=False)
    history: Mapped["History"] = relationship(
        "History", back_populates="picture", lazy="joined", cascade="all, delete"
    )


class Role(enum.Enum):
    """Enumeration class representing user roles in the FastAPI application."""

    admin: str = "admin"
    user: str = "user"


user_car_association = Table(
    "user_car_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("car_id", Integer, ForeignKey("cars.id")),
)


class User(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'users' table in the database."""

    __tablename__ = "users"
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=True, unique=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=True
    )
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)
    blacklisted_tokens: Mapped["Blacklisted"] = relationship(
        "Blacklisted", back_populates="user", lazy='joined', uselist=True
    )
    cars: Mapped[List["Car"]] = relationship(
        secondary=user_car_association, back_populates="users", lazy="joined"
    )


class Blacklisted(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'blacklisted_tokens' table in the database."""

    __tablename__ = "blacklisted"
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship(
        "User", back_populates="blacklisted_tokens", lazy="joined", cascade="all, delete"
    )


class Car(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'cars' table in the database."""

    __tablename__ = "cars"
    credit: Mapped[float] = mapped_column(Float, nullable=True)
    plate: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    model: Mapped[str] = mapped_column(String(128), nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)

    history: Mapped["History"] = relationship(
        "History", back_populates="car", lazy="joined", cascade="all, delete"
    )
    users: Mapped[List["User"]] = relationship(
        secondary=user_car_association, back_populates="cars", lazy="joined"
    )


class ParkingRate(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'parking_rates' table in the database."""

    __tablename__ = "parking_rates"
    rate_per_hour: Mapped[float] = mapped_column(Float, default=10.0, nullable=True)
    rate_per_day: Mapped[float] = mapped_column(Float, default=5.0, nullable=True)
    number_of_spaces: Mapped[int] = mapped_column(Integer, default=100, nullable=True)
    history: Mapped["History"] = relationship(
        "History", back_populates="rates", lazy="joined", cascade="all, delete",
    )

class History(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'history' table in the database."""

    __tablename__ = "history"
    entry_time: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    exit_time: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    parking_time: Mapped[float] = mapped_column(Float, nullable=True)
    cost: Mapped[float] = mapped_column(Float, nullable=True)
    paid: Mapped[bool] = mapped_column(default=False, nullable=True)
    number_free_spaces: Mapped[int] = mapped_column(Integer, nullable=True)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.id"))
    picture_id: Mapped[int] = mapped_column(Integer, ForeignKey("pictures.id"))
    rate_id: Mapped[int] = mapped_column(Integer, ForeignKey("parking_rates.id"))
    
    car: Mapped["Car"] = relationship(
        "Car",
        back_populates="history",
        lazy="joined",
        cascade="all, delete",
    )
    picture: Mapped["Picture"] = relationship(
        "Picture",
        back_populates="history",
        lazy="joined",
        cascade="all, delete",
    )
    rates: Mapped["ParkingRate"] = relationship(
        "ParkingRate",
        back_populates="history",
        lazy="joined",
        cascade="all, delete",
    )
