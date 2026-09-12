from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# Location Schemas
class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(hospital|shelter|critical_infrastructure)$")
    address: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    capacity: Optional[int] = Field(None, ge=0)
    current_occupancy: int = Field(0, ge=0)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    is_active: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(hospital|shelter|critical_infrastructure)$")
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    capacity: Optional[int] = Field(None, ge=0)
    current_occupancy: Optional[int] = Field(None, ge=0)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    location_id: int
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    alert_type: str = Field(..., pattern="^(flood_warning|evacuation_order|all_clear)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    water_level: Optional[float] = Field(None, ge=0)
    predicted_peak: Optional[float] = Field(None, ge=0)
    affected_population: Optional[int] = Field(None, ge=0)
    recommended_action: str = Field(..., min_length=1)
    justification: str = Field(..., min_length=1)
    issued_by: str = Field(..., min_length=1, max_length=255)
    expires_at: Optional[datetime] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    alert_type: Optional[str] = Field(None, pattern="^(flood_warning|evacuation_order|all_clear)$")
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    water_level: Optional[float] = Field(None, ge=0)
    predicted_peak: Optional[float] = Field(None, ge=0)
    affected_population: Optional[int] = Field(None, ge=0)
    recommended_action: Optional[str] = Field(None, min_length=1)
    justification: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(active|resolved|expired)$")
    expires_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertResponse(AlertBase):
    id: int
    status: str
    issued_at: datetime
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
