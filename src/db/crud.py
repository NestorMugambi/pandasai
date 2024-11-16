from typing import List, Optional
from sqlalchemy.orm import Session
from src.db.models import UploadedFile

class FileCRUD:
    def __init__(self, db: Session):
        """
        Initialize with a database session.
        """
        self.db = db

    def get_file_paths(self, file_id: Optional[int] = None) -> List[str]:
        """
        Get file paths from the database.
        - If `file_id` is provided, return the file path of that file as an array.
        - If no `file_id` is provided, return paths of all files.
        """
        if file_id:
            # Query the database for the specific file by id
            file = self.db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
            if not file:
                return []  # Return an empty list if file not found
            return [file.file_path]  # Return as a list

        # Query the database for all files
        files = self.db.query(UploadedFile).all()
        return [file.file_path for file in files]
    
    def get_all_files_metadata(self) -> List[dict]:
        """
        Get metadata for all files.
        Returns a list of dictionaries containing file metadata.
        """
        files = self.db.query(UploadedFile).all()
        return [
            {
                "id": file.id,
                "description": file.description,
                "file_path": file.file_path,                
            }
            for file in files
        ]
