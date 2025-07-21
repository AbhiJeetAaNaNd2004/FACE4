#!/usr/bin/env python3
"""
Database Initialization Script for Face Recognition Attendance System
Creates tables and inserts sample data
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from db.db_config import create_tables, get_db, test_connection
from db.db_models import Employee, UserAccount, CameraConfig, Department
from app.security import get_password_hash
from datetime import date
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with tables and sample data"""
    
    print("Database Initialization - Face Recognition Attendance System")
    print("=" * 70)
    
    # Test database connection first
    print("Testing database connection...")
    if not test_connection():
        print("ERROR: Database connection failed. Please check your configuration.")
        return False
    
    print("SUCCESS: Database connection successful")
    
    # Create tables
    print("Creating database tables...")
    try:
        create_tables()
        print("SUCCESS: Database tables created successfully")
    except Exception as e:
        print(f"ERROR: Error creating tables: {e}")
        return False
    
    # Insert sample data
    print("Inserting sample data...")
    
    db = next(get_db())
    try:
        # Create sample departments first
        existing_dept = db.query(Department).filter(Department.name == "Engineering").first()
        if not existing_dept:
            departments = [
                Department(
                    name="Engineering",
                    description="Software development and technical operations"
                ),
                Department(
                    name="Human Resources",
                    description="Employee management and organizational development"
                ),
                Department(
                    name="Administration",
                    description="General administration and support services"
                )
            ]
            
            for dept in departments:
                db.add(dept)
            
            # Commit departments first so we can reference them
            db.commit()
            print("SUCCESS: Created sample departments")
        else:
            print("INFO: Sample departments already exist")
        
        # Get department IDs for employee creation
        eng_dept = db.query(Department).filter(Department.name == "Engineering").first()
        hr_dept = db.query(Department).filter(Department.name == "Human Resources").first()
        
        # Check if sample employees exist
        existing_employee = db.query(Employee).filter(Employee.employee_id == "EMP001").first()
        if not existing_employee:
            # Create sample employees
            employees = [
                Employee(
                    employee_id="EMP001",
                    name="John Doe",
                    department_id=eng_dept.id,
                    role="Software Developer",
                    date_joined=date(2023, 1, 15),
                    email="john.doe@company.com",
                    phone="+1234567890",
                    is_active=True
                ),
                Employee(
                    employee_id="EMP002",
                    name="Jane Smith",
                    department_id=hr_dept.id,
                    role="HR Manager",
                    date_joined=date(2023, 2, 1),
                    email="jane.smith@company.com",
                    phone="+1234567891",
                    is_active=True
                ),
                Employee(
                    employee_id="EMP003",
                    name="Mike Johnson",
                    department_id=eng_dept.id,
                    role="Senior Developer",
                    date_joined=date(2023, 3, 10),
                    email="mike.johnson@company.com",
                    phone="+1234567892",
                    is_active=True
                )
            ]
            
            for employee in employees:
                db.add(employee)
            
            # Commit employees before creating user accounts
            db.commit()
            print("SUCCESS: Created sample employees")
        else:
            print("INFO: Sample employees already exist")
        
        # Create user accounts for all roles (after employees are created)
        users_to_create = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "super_admin",
                "employee_id": None,
                "description": "Super Admin user"
            },
            {
                "username": "hr_manager",
                "password": "hr123",
                "role": "admin",
                "employee_id": "EMP002",
                "description": "Admin user (HR Manager)"
            },
            {
                "username": "john.doe",
                "password": "john123",
                "role": "employee",
                "employee_id": "EMP001",
                "description": "Employee user (John Doe)"
            },
            {
                "username": "mike.johnson",
                "password": "mike123",
                "role": "employee",
                "employee_id": "EMP003",
                "description": "Employee user (Mike Johnson)"
            }
        ]
        
        for user_data in users_to_create:
            existing_user = db.query(UserAccount).filter(UserAccount.username == user_data["username"]).first()
            if not existing_user:
                # Create user account
                user = UserAccount(
                    username=user_data["username"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    employee_id=user_data["employee_id"],
                    is_active=True
                )
                db.add(user)
                print(f"SUCCESS: Created {user_data['description']} (username: {user_data['username']}, password: {user_data['password']})")
            else:
                print(f"INFO: User {user_data['username']} already exists")
        
        # Check if sample camera exists
        existing_camera = db.query(CameraConfig).filter(CameraConfig.camera_id == 0).first()
        if not existing_camera:
            # Create sample camera configuration
            camera = CameraConfig(
                camera_id=0,
                name="Main Entrance Camera",
                camera_type="entry",
                resolution_width=640,
                resolution_height=480,
                fps=30,
                status="active",
                is_active=True,
                location_description="Main entrance door"
            )
            db.add(camera)
            print("SUCCESS: Created sample camera configuration")
        else:
            print("INFO: Sample camera already exists")
        
        # Commit all changes
        db.commit()
        print("SUCCESS: Sample data inserted successfully")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: Error inserting sample data: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function"""
    print("Starting database initialization...")
    
    success = initialize_database()
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("=" * 70)
        print("📋 Summary:")
        print("   • Database tables created")
        print("   • Sample departments added")
        print("   • Sample employees added")
        print("   • Sample camera configuration added")
        print("   • User accounts created for all roles")
        print("=" * 70)
        print("🔑 Login Credentials:")
        print("   Super Admin: admin / admin123")
        print("   Admin (HR):  hr_manager / hr123") 
        print("   Employee:    john.doe / john123")
        print("   Employee:    mike.johnson / mike123")
        print("=" * 70)
        print("SUCCESS: You can now start the server!")
    else:
        print("\nERROR: Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()