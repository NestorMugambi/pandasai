from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import os
from typing import Optional

from src.db.models import UploadedFile, SessionLocal
from src.db.database import get_db
from src.db.crud import FileCRUD

app = FastAPI()

# Directory to save uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-file/")
async def upload_file(
    description: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # Validate file type 
    if not file.filename.endswith("csv"):
        raise HTTPException(status_code=400, detail="Only csv files are allowed.")

    # Save the file locally
    file_path = Path(UPLOAD_DIR) / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Save file metadata in the database
    new_file = UploadedFile(
        description=description,
        file_path=str(file_path.resolve())
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
    "id": new_file.id,
    "description": new_file.description,
    "file_path": [new_file.file_path],  
}

@app.get("/files/")
def get_files(file_id: Optional[int] = None, db: Session = Depends(get_db)):
    file_crud = FileCRUD(db)  # Create an instance of the CRUD class
    file_paths = file_crud.get_file_paths(file_id)  # Call the synchronous method

    if not file_paths:
        raise HTTPException(status_code=404, detail="File(s) not found.")

    return {"file_paths": file_paths}

@app.get("/files/metadata/")
def get_files_metadata(db: Session = Depends(get_db)):
    """
    Retrieve metadata for all files.
    """
    file_crud = FileCRUD(db)
    metadata = file_crud.get_all_files_metadata()

    if not metadata:
        raise HTTPException(status_code=404, detail="No files found.")

    return {"files": metadata}
