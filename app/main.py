from fastapi import FastAPI
from products.routers import router as product_router
from database.db import engine, Base
import asyncio

app = FastAPI()

app.include_router(product_router)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_tables()
    print("Таблицы успешно созданы")

@app.get("/")
async def root():
    return {"message": "Welcome to the Shop API"}