import datetime
from typing import Optional, List
from pydantic import BaseModel


class StadiumModel(BaseModel):
    name: str
    description: str = ''
    image_url: List[str] = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f" \
                           "/Example_image.svg/600px-Example_image.svg.png"
    price: float = 0.0
    opening_time: Optional[str] = "08:00:00"
    closing_time: Optional[str] = "00:00:00"
    is_active: Optional[bool] = True
    region: str = "Tashkent"
    district: str = "Yakka Saroy"
    location: dict = {"longitude": 0, "latitude": 0}


class OrderModel(BaseModel):
    status: str = "PENDING"
    stadium_id: int = 0
    start_time: Optional[datetime.datetime]
    hour: float = 1.0
