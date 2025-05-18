from fastapi import FastAPI
from products.routers import router as product_router

app = FastAPI()

app.include_router(product_router)