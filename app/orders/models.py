from pydantic import BaseModel, EmailStr, validator, Field, conint
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0, description="ID товара должен быть положительным числом")
    quantity: conint(gt=0, le=100) = Field(..., description="Количество от 1 до 100")

class OrderStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=50, example="Иван")
    customer_surname: str = Field(..., min_length=2, max_length=50, example="Иванов")
    customer_email: EmailStr = Field(..., example="user@example.com")
    customer_phone: str = Field(..., min_length=5, max_length=20, example="+79161234567")
    delivery_country: str = Field(..., min_length=2, max_length=50, example="Россия")
    delivery_city: str = Field(..., min_length=2, max_length=50, example="Москва")
    delivery_street: str = Field(..., min_length=2, max_length=100, example="Ленина")
    delivery_building: str = Field(..., min_length=1, max_length=20, example="42")
    items: List[OrderItem] = Field(..., min_items=1, description="Список товаров")

    @validator('customer_phone')
    def validate_phone(cls, v):
        if not v.replace('+', '').isdigit():
            raise ValueError('Номер телефона должен содержать только цифры')
        return v

class OrderResponse(BaseModel):
    order_id: int = Field(..., example=1001)
    customer_name: str = Field(..., example="Иван")
    customer_surname: str = Field(..., example="Иванов")
    status: OrderStatus = Field(..., example="created")
    created_at: datetime = Field(..., example="2023-07-20T12:00:00")
    total_items: int = Field(..., ge=1, example=2)
    total_amount: Optional[float] = Field(None, ge=0, example=1999.98)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "order_id": 1001,
                "customer_name": "Иван",
                "customer_surname": "Иванов",
                "status": "created",
                "created_at": "2023-07-20T12:00:00",
                "total_items": 2,
                "total_amount": 1999.98
            }
        }