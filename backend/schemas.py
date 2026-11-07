from pydantic import BaseModel, EmailStr
from typing import Optional
from models import RoleEnum

class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: Optional[RoleEnum] = RoleEnum.estudiante

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: RoleEnum
    avatar: Optional[str]
    nivel: int
    xp: int
    monedas: int
    vidas: int
    racha: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    avatar: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class ExerciseCreate(BaseModel):
    titulo: str
    descripcion: str
    ejemplo_codigo: Optional[str] = None
    respuesta_correcta: str
    xp_recompensa: int
    nivel_requerido: int

class ExerciseResponse(ExerciseCreate):
    id: int

    class Config:
        from_attributes = True

class ProgressCreate(BaseModel):
    ejercicio_id: int
    completado: bool

class ProgressResponse(BaseModel):
    id: int
    usuario_id: int
    ejercicio_id: int
    completado: bool

    class Config:
        from_attributes = True

class MonsterUpdate(BaseModel):
    ojos: Optional[str] = None
    boca: Optional[str] = None
    color: Optional[str] = None
    accesorio: Optional[str] = None
