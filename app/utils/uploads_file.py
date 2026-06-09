import os
import shutil
import uuid
from fastapi import File, HTTPException, UploadFile, status

MEDIA_DIR = "app/media"


# def upload_bytes(file: bytes = File(...)):
#     return {
#         "filename": "archivo_subido",
#         "size_bytes": len(file)
#     }
    
# def upload_file(file: UploadFile = File(...)):
#     return {
#         "filename": file.filename,
#         "size_bytes": len(file.file.read())
#     }
    
def ensure_media_dir_exists():
    os.makedirs(MEDIA_DIR, exist_ok=True)
    
def save_uploaded_img(file: UploadFile) -> dict:
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen")
    
    ensure_media_dir_exists()
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}",
        "size_bytes": os.path.getsize(file_path)
    }