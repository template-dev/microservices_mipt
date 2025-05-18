import os
import aiofiles
from fastapi import UploadFile
from typing import Optional


os.makedirs("uploads/products", exist_ok=True)


async def save_upload_file(upload_file: UploadFile, product_id: int) -> Optional[str]:
    try:
        file_ext = upload_file.filename.split(".")[-1]
        filename = f"product_{product_id}.{file_ext}"
        file_path = os.path.join("uploads", "products", filename)
        
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await upload_file.read()
            await buffer.write(content)
        
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


async def delete_upload_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False