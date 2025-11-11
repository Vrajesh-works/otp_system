"""
Seed data script for testing
Creates default SMS templates
"""
from database import SessionLocal, engine, Base
from models import SMSTemplate
from datetime import datetime

def seed_database():
    """Populate database with initial test data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if templates already exist
        existing_templates = db.query(SMSTemplate).count()
        if existing_templates > 0:
            print("Database already seeded. Skipping...")
            return
        
        # Create SMS templates
        templates = [
            SMSTemplate(
                template_type="login",
                template_content="Your login OTP is {otp}. Valid for 5 minutes. Do not share this code.",
                is_active=True
            ),
            SMSTemplate(
                template_type="registration",
                template_content="Welcome! Your registration OTP is {otp}. This code expires in 5 minutes.",
                is_active=True
            ),
            SMSTemplate(
                template_type="password_reset",
                template_content="Password reset OTP: {otp}. Valid for 5 minutes. If you didn't request this, ignore this message.",
                is_active=True
            ),
            SMSTemplate(
                template_type="transaction",
                template_content="Transaction verification code: {otp}. Valid for 5 minutes. Do not share with anyone.",
                is_active=True
            )
        ]
        
        # Add templates to database
        for template in templates:
            db.add(template)
        
        db.commit()
        print("✅ Database seeded successfully!")
        print(f"✅ Created {len(templates)} SMS templates")
        
        # Display created templates
        print("\n📋 Created Templates:")
        for template in templates:
            print(f"  - {template.template_type}: {template.template_content[:50]}...")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding database...")
    seed_database()