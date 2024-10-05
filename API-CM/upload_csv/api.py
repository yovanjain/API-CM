from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from db_module.connection import get_db
from models import CompanyProfile
from utils.services import app_logger  # Assuming app_logger is correctly configured
from utils.basic_auth import get_current_user
from utils.config import Settings
import os
from utils.helper import process_csv_in_background
from fastapi.responses import JSONResponse
import aiofiles

settings = Settings()

csv_router = APIRouter(
    prefix="/upload_csv", tags=["Upload CSV"], responses={422: {"description": "Not Found"}}
)


@csv_router.post("/upload-csv/")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        app_logger.info(f"User {current_user['username']} is uploading file: {file.filename}")
        
        # Check if the file is a CSV
        if not file.filename.endswith('.csv'):
            app_logger.warning(f"File {file.filename} is not a CSV. Upload aborted.")
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Define the file path
        file_path = os.path.join(settings.PROJECT_FILE_DIR, file.filename)
        app_logger.info(f"Saving file to {file_path}")
        
        # Save the file asynchronously
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read() 
            await out_file.write(content)
        
        app_logger.info(f"File {file.filename} saved successfully.")
        
        # Add background task to process the CSV file
        background_tasks.add_task(process_csv_in_background, file_path)
        app_logger.info(f"Background task added to process the CSV file: {file.filename}")

        return JSONResponse(content={"message": "File uploaded successfully, processing in background."})
    
    except Exception as e:
        error_message = f"Error occurred during file upload: {str(e)}"
        app_logger.error(f"{error_message}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading the file.")
