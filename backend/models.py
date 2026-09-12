from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base


class Location(Base):
    """Vulnerable location model for tracking hospitals, shelters, and critical infrastructure"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # hospital, shelter, critical_infrastructure
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=True)
    current_occupancy = Column(Integer, default=0)
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = relationship("Alert", back_populates="location")


class Alert(Base):
    """Flood alert model for tracking emergency notifications and decisions"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    alert_type = Column(String(50), nullable=False)  # flood_warning, evacuation_order, all_clear
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    water_level = Column(Float, nullable=True)
    predicted_peak = Column(Float, nullable=True)
    affected_population = Column(Integer, nullable=True)
    recommended_action = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)
    status = Column(String(20), default="active")  # active, resolved, expired
    issued_by = Column(String(255), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="alerts")
