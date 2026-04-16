from pathlib import Path
from typing import BinaryIO
import shutil


async def save_upload_file(file: BinaryIO, filename: str, upload_dir: str = "data/uploads") -> str:
      """Save uploaded file safely and return path."""
      upload_path = Path(upload_dir)
      upload_path.mkdir(parents=True, exist_ok=True)


      file_path = upload_path / filename
      with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)

      return str(file_path)
