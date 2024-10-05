from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db_module.connection import get_db
from models import CompanyProfile
from utils.services import app_logger  # Assuming app_logger is properly initialized
import traceback
from sqlalchemy.exc import IntegrityError
from utils.basic_auth import get_current_user
from fastapi.responses import JSONResponse

query_router = APIRouter(
    prefix="/query", tags=["Query Builder"], responses={422: {"description": "Not Found"}}
)


@query_router.get("/company-profiles/")
async def query_company_profiles(
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    year_founded: Optional[int] = Query(None, description="Filter by year founded"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Log the start of the request
        app_logger.info(f"Starting query for company profiles with user {current_user['username']}")
        
        # Build the query
        query = db.query(func.count(CompanyProfile.id))
        
        if first_name:
            query = query.filter(CompanyProfile.first_name.ilike(f"%{first_name}%"))
            app_logger.info(f"Filtering by first_name: {first_name}")
        
        if city:
            query = query.filter(CompanyProfile.city.ilike(f"%{city}%"))
            app_logger.info(f"Filtering by city: {city}")
        
        if state:
            query = query.filter(CompanyProfile.state.ilike(f"%{state}%"))
            app_logger.info(f"Filtering by state: {state}")
        
        if country:
            query = query.filter(CompanyProfile.country.ilike(f"%{country}%"))
            app_logger.info(f"Filtering by country: {country}")
        
        if industry:
            query = query.filter(CompanyProfile.industry.ilike(f"%{industry}%"))
            app_logger.info(f"Filtering by industry: {industry}")
        
        if year_founded:
            query = query.filter(CompanyProfile.year_founded == year_founded)
            app_logger.info(f"Filtering by year_founded: {year_founded}")
        
        # Execute the query
        count = query.scalar()

        if count == 0:
            app_logger.warning(f"No matching company profiles found for the provided filters.")
            raise HTTPException(status_code=404, detail="No matching company profiles found")
        
        # Log the count result
        app_logger.info(f"Found {count} matching company profiles.")
        return {"count": count}

    except IntegrityError as e:
        # Handle database-related errors
        error_message = f"Database Integrity Error: {str(e)}"
        app_logger.error(f"{error_message}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error while querying the database.")

    except Exception as e:
        # General exception handling
        error_message = f"Unexpected error: {str(e)}"
        app_logger.error(f"{error_message}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
