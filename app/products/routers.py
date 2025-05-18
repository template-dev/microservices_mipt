from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
import os
from . import models, schemas
from .file_utils import save_upload_file, delete_upload_file
from typing import Optional, List
from database.db import AsyncSessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import delete as sqlalchemy_delete


router = APIRouter(prefix="/products", tags=["Products"])


async def get_db():
    db = await AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Product)
async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    product_data = {
        "name": name,
        "description": description,
        "price": price
    }
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    if image:
        image_path = await save_upload_file(image, db_product.id)
        if image_path:
            db_product.image_path = image_path
            db.commit()
            db.refresh(db_product)
    
    product_response = schemas.Product.from_orm(db_product)
    if db_product.image_path:
        product_response.image_url = f"/static/products/{os.path.basename(db_product.image_path)}"
    
    return product_response


@router.get("/", response_model=list[schemas.Product])
async def get_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(select(models.Product).offset(skip).limit(limit))
    products = result.scalars().all()
    
    for product in products:
        if product.image_path:
            product.image_url = f"/static/products/{os.path.basename(product.image_path)}"
    return products


@router.get("/{product_id}", response_model=schemas.Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    if product.image_path:
        product.image_url = f"/static/products/{os.path.basename(product.image_path)}"
    
    return product


@router.put("/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    db_product = result.scalar_one_or_none()
    
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    if name is not None:
        db_product.name = name
    if description is not None:
        db_product.description = description
    if price is not None:
        db_product.price = price
    
    if image:
        if db_product.image_path:
            await delete_upload_file(db_product.image_path)
        
        image_path = await save_upload_file(image, product_id)
        if image_path:
            db_product.image_path = image_path
    
    await db.commit()
    await db.refresh(db_product)
    
    product_response = schemas.Product.from_orm(db_product)
    if db_product.image_path:
        product_response.image_url = f"/static/products/{os.path.basename(db_product.image_path)}"
    
    return product_response


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    db_product = result.scalar_one_or_none()
    
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    if db_product.image_path:
        await delete_upload_file(db_product.image_path)
    
    await db.execute(sqlalchemy_delete(models.Product).where(models.Product.id == product_id))
    await db.commit()
    
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_products(db: Session = Depends(get_db)):
    result = await db.execute(select(models.Product))
    products = result.scalars().all()
    
    for product in products:
        if product.image_path:
            await delete_upload_file(product.image_path)
    
    await db.execute(sqlalchemy_delete(models.Product))
    await db.commit()
    
    return None