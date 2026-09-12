from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database import get_db
from backend.models import Location
from backend.schemas import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new vulnerable location"""
    try:
        db_location = Location(**location.model_dump())
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        logger.info(f"Created location: {db_location.name} (ID: {db_location.id})")
        return db_location
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create location"
        )


@router.get("/", response_model=List[LocationResponse])
def get_locations(
    skip: int = 0,
    limit: int = 100,
    type: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Get all locations with optional filtering"""
    try:
        query = db.query(Location)
        
        if type:
            query = query.filter(Location.type == type)
        if is_active is not None:
            query = query.filter(Location.is_active == is_active)
        
        locations = query.offset(skip).limit(limit).all()
        return locations
    except Exception as e:
        logger.error(f"Error fetching locations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch locations"
        )


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found"
        )
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_update: LocationUpdate,
    db: Session = Depends(get_db)
):
    """Update a location"""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found"
        )
    
    try:
        update_data = location_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_location, field, value)
        
        db.commit()
        db.refresh(db_location)
        logger.info(f"Updated location: {db_location.name} (ID: {db_location.id})")
        return db_location
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update location"
        )


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Delete a location"""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found"
        )
    
    try:
        db.delete(db_location)
        db.commit()
        logger.info(f"Deleted location: {db_location.name} (ID: {location_id})")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete location"
        )
