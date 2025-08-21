from loader import appFA
from fastapi.responses import FileResponse


@appFA.get("/images/{filename}")
async def get_image(filename: str):
    return FileResponse(f"../../data/photo/{filename}")
