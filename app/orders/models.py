from sqlalchemy import Column, Integer, String, JSON, DateTime
from app.database.db import Base
from datetime import datetime
from enum import Enum as SqlEnum

class OrderStatus(str, SqlEnum):
    CREATED = "created"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(50))
    customer_surname = Column(String(50))
    customer_email = Column(String(100))
    customer_phone = Column(String(20))
    delivery_country = Column(String(50))
    delivery_city = Column(String(50))
    delivery_street = Column(String(100))
    delivery_building = Column(String(20))
    items = Column(JSON)
    status = Column(String(20), default=OrderStatus.CREATED)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(36))