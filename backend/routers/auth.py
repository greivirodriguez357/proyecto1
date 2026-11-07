from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_pycods_tea")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    hashed_pwd = pwd_context.hash(user.password)
    new_user = models.User(
        nombre=user.nombre,
        email=user.email,
        hashed_password=hashed_pwd,
        rol=user.rol
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user.email, "rol": user.rol.value})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Devuelve el usuario dueño del token JWT (Authorization: Bearer ...)."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión no válida o expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None:
        raise unauthorized
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise unauthorized
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise unauthorized
    return user


def require_roles(*roles: str):
    def checker(user: models.User = Depends(get_current_user)):
        if user.rol.value not in roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        return user
    return checker


@router.get("/me", response_model=schemas.UserResponse)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
