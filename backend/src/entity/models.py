import enum
from datetime import date

from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the FastAPI application."""

    pass


class TimeStampMixin(Base):
    """Mixin class providing timestamp information (created_at, updated_at) for SQLAlchemy models."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True
    )
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )


class Picture(TimeStampMixin):
    """SQLAlchemy model representing the 'pictures' table in the database."""

    __tablename__ = "pictures"
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="pictures", lazy="joined", cascade="all, delete"
    )


class Role(enum.Enum):
    """Enumeration class representing user roles in the FastAPI application."""

    admin: str = "admin"
    user: str = "user"


class User(TimeStampMixin):
    """SQLAlchemy model representing the 'users' table in the database."""

    __tablename__ = "users"
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(150), nullable=False)
    telegram: Mapped[str] = mapped_column(String(150), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=True
    )

    car: Mapped["Car"] = relationship(
        "Car", back_populates="user", uselist=True, lazy="joined", cascade="all, delete"
    )
    history: Mapped["History"] = relationship(
        "History",
        back_populates="user",
        uselist=True,
        lazy="joined",
        cascade="all, delete",
    )


class Car(TimeStampMixin):
    __tablename__ = "cars"
    plate: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    model: Mapped[str] = mapped_column(String(128), nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    blacklisted_tokens: Mapped["Blacklisted"] = relationship(
        "Blacklisted", back_populates="user", lazy="joined", cascade="all, delete"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="cars", lazy="joined", cascade="all, delete"
    )


class Blacklisted(TimeStampMixin):
    """SQLAlchemy model representing the 'blacklisted' table in the database."""

    __tablename__ = "blacklisted"
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.id"), nullable=True)
    car: Mapped["Car"] = relationship(
        "Car", back_populates="blacklisted_tokens", lazy="joined", cascade="all, delete"
    )


class ParkingRate(TimeStampMixin):
    __tablename__ = "parking_rates"
    rate_per_hour: Mapped[float] = mapped_column(Float, default=10, nullable=True)
    rate_per_day: Mapped[float] = mapped_column(Float, default=150, nullable=True)
    number_of_spaces: Mapped[int] = mapped_column(Integer, default=100, nullable=True)
    number_free_spaces: Mapped[int] = mapped_column(Integer, nullable=True)


class History(TimeStampMixin):
    """SQLAlchemy model representing the 'history' table in the database."""

    __tablename__ = "history"
    plate_number: Mapped[str] = mapped_column(
        String(50), ForeignKey("cars.plate"), nullable=False
    )
    entry_time: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    exit_time: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    parking_time: Mapped[float] = mapped_column(Float, nullable=True)
    cost: Mapped[float] = mapped_column(Float, nullable=True)
    paid: Mapped[bool] = mapped_column(default=False, nullable=True)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.id"))
    picture_id: Mapped[int] = mapped_column(Integer, ForeignKey("pictures.id"))
    rate_per_hour: Mapped[int] = mapped_column(
        Integer, ForeignKey("parking_rates.rate_per_hour")
    )
    rate_per_day: Mapped[int] = mapped_column(
        Integer, ForeignKey("parking_rates.rate_per_day")
    )
    car: Mapped["Car"] = relationship(
        "Car",
        back_populates="history",
        uselist=True,
        lazy="joined",
        cascade="all, delete",
    )
    pictures: Mapped["Picture"] = relationship(
        "Picture",
        back_populates="history",
        uselist=True,
        lazy="joined",
        cascade="all, delete",
    )
    rates: Mapped["ParkingRate"] = relationship(
        "ParkingRate",
        back_populates="history",
        uselist=True,
        lazy="joined",
        cascade="all, delete",
    )
