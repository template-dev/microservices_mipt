from fastapi import FastAPI
from app.orders.routers import router as orders_router
from app.database.db import engine, Base
import asyncio

app = FastAPI()

app.include_router(orders_router)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_tables()
    print("Tables have been created successfully")