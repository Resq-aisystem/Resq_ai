from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database import get_db
from backend.models import Alert, Location
from backend.schemas import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new flood alert"""
    # Verify location exists
    location = db.query(Location).filter(Location.id == alert.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {alert.location_id} not found"
        )
    
    try:
        db_alert = Alert(**alert.model_dump())
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        logger.info(f"Created alert: {db_alert.title} (ID: {db_alert.id}) for location {location.name}")
        return db_alert
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert"
        )


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 100,
    location_id: int = None,
    severity: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filtering"""
    try:
        query = db.query(Alert)
        
        if location_id:
            query = query.filter(Alert.location_id == location_id)
        if severity:
            query = query.filter(Alert.severity == severity)
        if status:
            query = query.filter(Alert.status == status)
        
        alerts = query.order_by(Alert.issued_at.desc()).offset(skip).limit(limit).all()
        return alerts
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alerts"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    try:
        update_data = alert_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_alert, field, value)
        
        db.commit()
        db.refresh(db_alert)
        logger.info(f"Updated alert: {db_alert.title} (ID: {db_alert.id})")
        return db_alert
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    try:
        db.delete(db_alert)
        db.commit()
        logger.info(f"Deleted alert: {db_alert.title} (ID: {alert_id})")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert"
        )
