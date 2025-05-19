from pydantic import BaseModel, EmailStr, validator
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_name: str
    customer_surname: str
    customer_email: EmailStr
    customer_phone: str
    delivery_country: str
    delivery_city: str
    delivery_street: str
    delivery_building: str
    items: List[OrderItem]

class OrderResponse(BaseModel):
    order_id: int
    customer_name: str
    customer_surname: str
    status: str
    created_at: datetime
    total_items: int

    class Config:
        from_attributes = True