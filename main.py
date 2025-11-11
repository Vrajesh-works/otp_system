"""
FastAPI OTP System with SMS Delivery Status Callbacks
Main application file
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
from pydantic import BaseModel, EmailStr, validator
from database import get_db, engine, Base
from models import OTP, SMSDeliveryStatus, SMSTemplate
from enum import Enum

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OTP System API",
    description="OTP generation, verification, and SMS delivery tracking",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"

class TemplateType(str, Enum):
    LOGIN = "login"
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    TRANSACTION = "transaction"

# Request/Response Models
class OTPGenerateRequest(BaseModel):
    phone_number: str
    template_type: TemplateType = TemplateType.LOGIN
    
    @validator('phone_number')
    def validate_phone(cls, v):
        # Remove spaces and dashes
        v = v.replace(" ", "").replace("-", "")
        if not v.startswith("+"):
            raise ValueError("Phone number must start with country code (+)")
        if len(v) < 10 or len(v) > 15:
            raise ValueError("Invalid phone number length")
        return v

class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
    
    @validator('otp_code')
    def validate_otp(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be 6 digits")
        return v

class SMSCallbackRequest(BaseModel):
    message_id: str
    status: DeliveryStatus
    timestamp: datetime
    error_message: Optional[str] = None

class OTPResponse(BaseModel):
    success: bool
    message: str
    otp_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    remaining_attempts: Optional[int] = None

class SMSTemplateCreate(BaseModel):
    template_type: TemplateType
    template_content: str
    
    @validator('template_content')
    def validate_template(cls, v):
        if "{otp}" not in v:
            raise ValueError("Template must contain {otp} placeholder")
        return v

class SMSTemplateResponse(BaseModel):
    id: int
    template_type: str
    template_content: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Helper Functions
def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def get_sms_template(db: Session, template_type: str) -> Optional[SMSTemplate]:
    """Get active SMS template"""
    return db.query(SMSTemplate).filter(
        SMSTemplate.template_type == template_type,
        SMSTemplate.is_active == True
    ).first()

def invalidate_previous_otps(db: Session, phone_number: str):
    """Invalidate all previous OTPs for a phone number"""
    db.query(OTP).filter(
        OTP.phone_number == phone_number,
        OTP.is_used == False,
        OTP.is_expired == False
    ).update({"is_expired": True})
    db.commit()

# API Endpoints

@app.get("/")
def read_root():
    return {
        "message": "OTP System API",
        "version": "1.0.0",
        "endpoints": {
            "generate_otp": "/api/otp/generate",
            "verify_otp": "/api/otp/verify",
            "sms_callback": "/api/sms/callback",
            "templates": "/api/templates"
        }
    }

@app.post("/api/otp/generate", response_model=OTPResponse)
def generate_otp(
    request: OTPGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new 6-digit OTP code and send via SMS
    - Invalidates previous unused OTPs for the phone number
    - OTP expires in 5 minutes
    - Returns OTP ID and expiration time
    """
    # Invalidate previous OTPs
    invalidate_previous_otps(db, request.phone_number)
    
    # Generate new OTP
    otp_code = generate_otp_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Get SMS template
    template = get_sms_template(db, request.template_type.value)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMS template not found for type: {request.template_type}"
        )
    
    # Create OTP record
    otp = OTP(
        phone_number=request.phone_number,
        otp_code=otp_code,
        expires_at=expires_at,
        attempts_remaining=3
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    # Create SMS delivery status record
    sms_message = template.template_content.replace("{otp}", otp_code)
    message_id = f"MSG_{otp.id}_{datetime.utcnow().timestamp()}"
    
    sms_status = SMSDeliveryStatus(
        otp_id=otp.id,
        message_id=message_id,
        phone_number=request.phone_number,
        message_content=sms_message,
        status="pending"
    )
    db.add(sms_status)
    db.commit()
    
    # TODO: Integrate with actual SMS provider (Twilio, AWS SNS, etc.)
    # send_sms(request.phone_number, sms_message, message_id)
    
    return OTPResponse(
        success=True,
        message="OTP generated and sent successfully",
        otp_id=otp.id,
        expires_at=expires_at,
        remaining_attempts=3
    )

@app.post("/api/otp/verify", response_model=OTPResponse)
def verify_otp(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP code
    - Maximum 3 attempts allowed
    - OTP must not be expired
    - OTP must not be already used
    """
    # Find the most recent valid OTP
    otp = db.query(OTP).filter(
        OTP.phone_number == request.phone_number,
        OTP.is_used == False,
        OTP.is_expired == False,
        OTP.expires_at > datetime.utcnow()
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid OTP found for this phone number"
        )
    
    # Check if attempts exhausted
    if otp.attempts_remaining <= 0:
        otp.is_expired = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum verification attempts exceeded"
        )
    
    # Verify OTP code
    if otp.otp_code != request.otp_code:
        otp.attempts_remaining -= 1
        db.commit()
        
        return OTPResponse(
            success=False,
            message="Invalid OTP code",
            remaining_attempts=otp.attempts_remaining
        )
    
    # OTP is valid
    otp.is_used = True
    otp.verified_at = datetime.utcnow()
    db.commit()
    
    return OTPResponse(
        success=True,
        message="OTP verified successfully",
        otp_id=otp.id
    )

@app.post("/api/sms/callback")
def sms_delivery_callback(
    callback: SMSCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle SMS delivery status callbacks from SMS provider
    - Updates delivery status in database
    - Tracks delivery timestamps
    """
    sms_status = db.query(SMSDeliveryStatus).filter(
        SMSDeliveryStatus.message_id == callback.message_id
    ).first()
    
    if not sms_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS message not found"
        )
    
    # Update status
    sms_status.status = callback.status.value
    sms_status.updated_at = datetime.utcnow()
    
    if callback.status == DeliveryStatus.DELIVERED:
        sms_status.delivered_at = callback.timestamp
    elif callback.status == DeliveryStatus.FAILED:
        sms_status.failed_at = callback.timestamp
        sms_status.error_message = callback.error_message
    
    db.commit()
    
    return {
        "success": True,
        "message": "Callback processed successfully",
        "message_id": callback.message_id,
        "status": callback.status.value
    }

@app.get("/api/sms/status/{message_id}")
def get_sms_status(message_id: str, db: Session = Depends(get_db)):
    """Get SMS delivery status by message ID"""
    sms_status = db.query(SMSDeliveryStatus).filter(
        SMSDeliveryStatus.message_id == message_id
    ).first()
    
    if not sms_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS message not found"
        )
    
    return {
        "message_id": sms_status.message_id,
        "phone_number": sms_status.phone_number,
        "status": sms_status.status,
        "sent_at": sms_status.created_at,
        "delivered_at": sms_status.delivered_at,
        "error_message": sms_status.error_message
    }

@app.post("/api/templates", response_model=SMSTemplateResponse)
def create_template(
    template: SMSTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new SMS template"""
    # Deactivate existing templates of same type
    db.query(SMSTemplate).filter(
        SMSTemplate.template_type == template.template_type.value
    ).update({"is_active": False})
    
    new_template = SMSTemplate(
        template_type=template.template_type.value,
        template_content=template.template_content,
        is_active=True
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template

@app.get("/api/templates", response_model=list[SMSTemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    """Get all SMS templates"""
    templates = db.query(SMSTemplate).filter(
        SMSTemplate.is_active == True
    ).all()
    return templates

@app.get("/api/templates/{template_type}", response_model=SMSTemplateResponse)
def get_template_by_type(
    template_type: TemplateType,
    db: Session = Depends(get_db)
):
    """Get SMS template by type"""
    template = get_sms_template(db, template_type.value)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found for type: {template_type}"
        )
    return template

@app.get("/api/otp/history/{phone_number}")
def get_otp_history(
    phone_number: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get OTP history for a phone number"""
    otps = db.query(OTP).filter(
        OTP.phone_number == phone_number
    ).order_by(OTP.created_at.desc()).limit(limit).all()
    
    return {
        "phone_number": phone_number,
        "total_otps": len(otps),
        "otps": [
            {
                "id": otp.id,
                "created_at": otp.created_at,
                "expires_at": otp.expires_at,
                "is_used": otp.is_used,
                "is_expired": otp.is_expired,
                "verified_at": otp.verified_at,
                "attempts_remaining": otp.attempts_remaining
            }
            for otp in otps
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)