from pydantic import BaseModel, EmailStr, validator, Field, conint
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: conint(gt=0, le=100)

class OrderStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_surname: str = Field(..., min_length=2)
    customer_email: EmailStr
    customer_phone: str = Field(..., min_length=5)
    delivery_country: str = Field(..., min_length=2)
    delivery_city: str = Field(..., min_length=2)
    delivery_street: str = Field(..., min_length=2)
    delivery_building: str = Field(..., min_length=1)
    items: List[OrderItem] = Field(..., min_items=1)

    @validator('customer_phone')
    def validate_phone(cls, v):
        if not v.replace('+', '').isdigit():
            raise ValueError('The number must contain only numbers.')
        return v

class OrderResponse(BaseModel):
    order_id: int
    customer_name: str
    customer_surname: str
    status: OrderStatus
    created_at: datetime
    total_items: int
    total_amount: Optional[float] = None

    class Config:
        from_attributes = True