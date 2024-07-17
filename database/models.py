from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import Table, Integer, ForeignKey, DateTime, Column
from typing import List
import json
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.dialects.sqlite import JSON


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(default="noob")
    telegram_id: Mapped[int] = mapped_column()
    number: Mapped[str] = mapped_column(unique=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_owner: Mapped[bool] = mapped_column(default=False)
    is_user: Mapped[bool] = mapped_column(default=True)
    lang: Mapped[str] = mapped_column(default="eng")

    stadiums: Mapped[List["Stadium"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class RegionEnum(Enum):
    name = "value"


class DistrictEnum(Enum):
    name = "value"


def create_enum_class(name, data):
    processed_data = [{"name": ''.join(e for e in item["name"] if e.isalnum()).lower()} for item in data]
    enum_class = Enum(name, [(item["name"].replace(" ", "_"), item["name"]) for item in processed_data])
    return enum_class


def populate_enums():
    from utils.config import regions_file_path
    with open(regions_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    RegionEnum = create_enum_class("RegionEnum", data["regions"])
    DistrictEnum = create_enum_class("DistrictEnum", data["districts"])


class Stadium(Base):
    __tablename__ = "stadium"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    image_urls: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(default=0.0)
    opening_time: Mapped[str] = mapped_column(default="08:00:00")
    closing_time: Mapped[str] = mapped_column(default="00:00:00")
    is_active: Mapped[bool] = mapped_column(default=False)
    region: Mapped[str] = mapped_column()
    district: Mapped[str] = mapped_column()
    location: Mapped[dict] = mapped_column(JSON, default={"longitude": 0, "latitude": 0})
    number_of_orders: Mapped[int] = mapped_column(default=0)
    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped["User"] = relationship(back_populates="stadiums")
    orders: Mapped["Order"] = relationship(back_populates="stadium")

    def set_image_urls(self, image_urls):
        self.image_urls = json.dumps(image_urls)

    def increment_order(self):
        self.number_of_orders += 1

    def get_image_urls(self):
        return json.loads(self.image_urls) if self.image_urls else []

    def __repr__(self):
        return f"<Stadium {self.name}>"


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    hour: Mapped[int] = mapped_column(default=1)

    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped["User"] = relationship(User, back_populates="orders")

    stadium_id: Mapped[int] = mapped_column(ForeignKey(Stadium.id), nullable=False)
    stadium: Mapped["Stadium"] = relationship(Stadium, back_populates="orders")

    @property
    def end_time(self):
        if self.start_time and self.hour is not None:
            return self.start_time + timedelta(hours=self.hour)
        return None

    def __repr__(self):
        return f"<Order order{self.id}>"

# class AvailableHour(Base):
#     __tablename__ = "available_hour"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     available_hour_start: Mapped[datetime] = mapped_column(nullable=False)
#     available_hour_end: Mapped[datetime] = mapped_column(nullable=False)
#
#     stadium_id: Mapped[int] = mapped_column(ForeignKey(Stadium.id), nullable=False)
#     stadium: Mapped["Stadium"] = relationship(Stadium, back_populates="available_hours")
#
#     def __repr__(self):
#         return f"<AvailableHour {self.available_hour_start} - {self.available_hour_end}>"
#

# etc..
# available_hours = relationship(
#     "AvailableHour",
#     secondary=stadium_available_hours_association,
#     primaryjoin="Stadium.id == stadium_available_hours_association.c.stadium_id",
#     secondaryjoin=(
#         "and_(stadium_available_hours_association.c.stadium_id == Stadium.id, "
#         "stadium_available_hours_association.c.available_hour_start <= func.now(), "
#         "stadium_available_hours_association.c.available_hour_end >= func.now())"
#     ),
#     back_populates="stadium"
# )
