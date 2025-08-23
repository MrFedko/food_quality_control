from loader import appFA
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path


PHOTO_DIR = Path("/Users/mac/Desktop/my_projects/quality_control/controlBot/data/photo")
@appFA.get("/image/{filename}")
async def get_image(filename: str):
    file_path = PHOTO_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
