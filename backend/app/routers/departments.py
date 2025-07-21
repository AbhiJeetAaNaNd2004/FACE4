"""
Department Management Router
Provides endpoints for managing departments (Super Admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas import CurrentUser, MessageResponse
from app.security import require_super_admin
from db.db_config import get_db
from db.db_models import Department
from pydantic import BaseModel
from utils.logging import get_logger

router = APIRouter(prefix="/departments", tags=["Department Management"])
logger = get_logger(__name__)

# Pydantic models for request/response
class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    employee_count: Optional[int] = 0

    class Config:
        from_attributes = True

@router.get("/", response_model=List[DepartmentResponse])
async def get_all_departments(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Get all departments (Super Admin only)
    """
    try:
        query = db.query(Department)
        if not include_inactive:
            query = query.filter(Department.is_active == True)
        
        departments = query.all()
        
        # Add employee count for each department
        result = []
        for dept in departments:
            dept_dict = {
                "id": dept.id,
                "name": dept.name,
                "description": dept.description,
                "is_active": dept.is_active,
                "created_at": dept.created_at,
                "updated_at": dept.updated_at,
                "employee_count": len(dept.employees) if dept.employees else 0
            }
            result.append(DepartmentResponse(**dept_dict))
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch departments"
        )

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Get a specific department by ID (Super Admin only)
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    dept_dict = {
        "id": department.id,
        "name": department.name,
        "description": department.description,
        "is_active": department.is_active,
        "created_at": department.created_at,
        "updated_at": department.updated_at,
        "employee_count": len(department.employees) if department.employees else 0
    }
    
    return DepartmentResponse(**dept_dict)

@router.post("/", response_model=DepartmentResponse)
async def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Create a new department (Super Admin only)
    """
    try:
        # Check if department name already exists
        existing_dept = db.query(Department).filter(Department.name == department.name).first()
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this name already exists"
            )
        
        # Create new department
        new_department = Department(
            name=department.name,
            description=department.description
        )
        
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        
        logger.info(f"Department '{department.name}' created by user {current_user.username}")
        
        dept_dict = {
            "id": new_department.id,
            "name": new_department.name,
            "description": new_department.description,
            "is_active": new_department.is_active,
            "created_at": new_department.created_at,
            "updated_at": new_department.updated_at,
            "employee_count": 0
        }
        
        return DepartmentResponse(**dept_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create department"
        )

@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_update: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Update a department (Super Admin only)
    """
    try:
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if new name conflicts with existing department
        if department_update.name and department_update.name != department.name:
            existing_dept = db.query(Department).filter(Department.name == department_update.name).first()
            if existing_dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department with this name already exists"
                )
        
        # Update fields
        if department_update.name is not None:
            department.name = department_update.name
        if department_update.description is not None:
            department.description = department_update.description
        if department_update.is_active is not None:
            department.is_active = department_update.is_active
        
        department.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(department)
        
        logger.info(f"Department '{department.name}' updated by user {current_user.username}")
        
        dept_dict = {
            "id": department.id,
            "name": department.name,
            "description": department.description,
            "is_active": department.is_active,
            "created_at": department.created_at,
            "updated_at": department.updated_at,
            "employee_count": len(department.employees) if department.employees else 0
        }
        
        return DepartmentResponse(**dept_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update department"
        )

@router.delete("/{department_id}", response_model=MessageResponse)
async def delete_department(
    department_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Delete a department (Super Admin only)
    Set force=true to delete department with employees (will also delete employees)
    """
    try:
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if department has employees
        if department.employees and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department has {len(department.employees)} employees. Use force=true to delete anyway."
            )
        
        department_name = department.name
        db.delete(department)
        db.commit()
        
        logger.info(f"Department '{department_name}' deleted by user {current_user.username}")
        
        return MessageResponse(
            success=True,
            message=f"Department '{department_name}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete department"
        )