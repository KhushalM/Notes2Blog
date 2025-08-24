import base64
import uuid
from pathlib import Path
from .config import settings
from typing import Tuple
from PIL import Image
import io


Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def save_upload(file: str, content: bytes) -> str:
    ext = Path(file).suffix or ".bin"
    safe = f"{uuid.uuid4().hex}{ext}"
    path = Path(settings.UPLOAD_DIR) / safe
    with open(path, "wb") as f:
        f.write(content)
    return safe

def save_output(file: str, content: str, subdir: str = "") -> str:
    out_dir = Path(settings.OUTPUT_DIR) / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / file
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)

def read_file(file: str) -> bytes:
    with open(file, "rb") as f:
        return f.read()

def as_base64(path: str, max_size: tuple = None, quality: int = None) -> str:
    """Convert image to base64 with compression to reduce token usage"""
    # If path is just a filename, assume it's in the uploads directory
    if not Path(path).is_absolute() and not str(path).startswith('./'):
        full_path = Path(settings.UPLOAD_DIR) / path
    else:
        full_path = Path(path)
    
    # Use config defaults if not specified
    max_size = max_size or settings.MAX_IMAGE_SIZE
    quality = quality or settings.IMAGE_QUALITY
    
    try:
        # Open and compress the image
        with Image.open(full_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Compress to JPEG in memory
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            compressed_data = buffer.getvalue()
            
            print(f"📏 Image compressed: {len(read_file(str(full_path)))} bytes → {len(compressed_data)} bytes")
            return base64.b64encode(compressed_data).decode("utf-8")
            
    except Exception as e:
        print(f"⚠️ Image compression failed, using original: {e}")
        # Fallback to original file
        data = read_file(str(full_path))
        return base64.b64encode(data).decode("utf-8")