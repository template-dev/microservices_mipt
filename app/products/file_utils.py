import os
import aiofiles
from fastapi import UploadFile
from typing import Optional


os.makedirs("uploads/products", exist_ok=True)


async def save_upload_file(upload_file: UploadFile, product_id: int):
    filename = f"product_{product_id}_{upload_file.filename}"
    filepath = os.path.join("uploads", filename)
    async with aiofiles.open(filepath, "wb") as buffer:
        await buffer.write(await upload_file.read())
    return filepath


async def delete_upload_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False