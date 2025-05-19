from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from typing import List
from datetime import datetime

from app.database.db import AsyncSessionLocal
from .schemas import OrderCreate, OrderResponse, OrderStatus
from .models import Order, OrderStatus as DBOrderStatus

router = APIRouter(prefix="/orders", tags=["Orders"])

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    x_session_id: str = Header(default=None),
    db: AsyncSession = Depends(get_db)
):
    db_order = Order(
        customer_name=order_data.customer_name,
        customer_surname=order_data.customer_surname,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        delivery_country=order_data.delivery_country,
        delivery_city=order_data.delivery_city,
        delivery_street=order_data.delivery_street,
        delivery_building=order_data.delivery_building,
        items=[item.dict() for item in order_data.items],
        status=DBOrderStatus.CREATED,
        session_id=x_session_id
    )
    
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    return OrderResponse(
        order_id=db_order.id,
        customer_name=db_order.customer_name,
        customer_surname=db_order.customer_surname,
        status=db_order.status,
        created_at=db_order.created_at,
        total_items=len(db_order.items),
        total_amount=sum(item['quantity'] * item.get('price', 0) for item in db_order.items)
    )

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: OrderStatus = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Order)
    
    if status:
        query = query.where(Order.status == status.value)
        
    result = await db.execute(
        query.order_by(Order.created_at.desc())
             .offset(skip)
             .limit(limit)
    )
    
    orders = result.scalars().all()
    
    return [
        OrderResponse(
            order_id=order.id,
            customer_name=order.customer_name,
            customer_surname=order.customer_surname,
            status=order.status,
            created_at=order.created_at,
            total_items=len(order.items),
            total_amount=sum(item['quantity'] * item.get('price', 0) for item in order.items)
        )
        for order in orders
    ]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return OrderResponse(
        order_id=order.id,
        customer_name=order.customer_name,
        customer_surname=order.customer_surname,
        status=order.status,
        created_at=order.created_at,
        total_items=len(order.items),
        total_amount=sum(item['quantity'] * item.get('price', 0) for item in order.items)
    )

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = new_status.value
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse(
        order_id=order.id,
        customer_name=order.customer_name,
        customer_surname=order.customer_surname,
        status=order.status,
        created_at=order.created_at,
        total_items=len(order.items),
        total_amount=sum(item['quantity'] * item.get('price', 0) for item in order.items)
    )

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await db.delete(order)
    await db.commit()