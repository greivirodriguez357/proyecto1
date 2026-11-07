from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from routers.auth import get_current_user, require_roles

router = APIRouter()

# IMPORTANTE: las rutas "/me" van antes que "/{user_id}"
@router.patch("/me", response_model=schemas.UserResponse)
def update_me(data: schemas.UserUpdate, db: Session = Depends(get_db),
              current_user: models.User = Depends(get_current_user)):
    if data.avatar is not None:
        current_user.avatar = data.avatar[:255]
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
              _: models.User = Depends(require_roles("admin", "docente"))):
    return db.query(models.User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db),
             _: models.User = Depends(require_roles("admin", "docente"))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
