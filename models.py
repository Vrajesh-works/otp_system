"""
Database models for OTP System
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class OTP(Base):
    """OTP storage with 5-minute expiration"""
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    attempts_remaining = Column(Integer, default=3, nullable=False)
    
    # Relationship
    sms_statuses = relationship("SMSDeliveryStatus", back_populates="otp")
    
    def __repr__(self):
        return f"<OTP(id={self.id}, phone={self.phone_number}, expires_at={self.expires_at})>"

class SMSDeliveryStatus(Base):
    """Track SMS delivery status with callbacks"""
    __tablename__ = "sms_delivery_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    otp_id = Column(Integer, ForeignKey("otps.id"), nullable=False)
    message_id = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    message_content = Column(Text, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, sent, delivered, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship
    otp = relationship("OTP", back_populates="sms_statuses")
    
    def __repr__(self):
        return f"<SMSDeliveryStatus(id={self.id}, message_id={self.message_id}, status={self.status})>"

class SMSTemplate(Base):
    """SMS message templates"""
    __tablename__ = "sms_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_type = Column(String(50), nullable=False, index=True)  # login, registration, password_reset, etc.
    template_content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SMSTemplate(id={self.id}, type={self.template_type}, active={self.is_active})>"