from sqlalchemy import UniqueConstraint, Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

class RoleEnum(str, enum.Enum):
    admin = "admin"
    docente = "docente"
    estudiante = "estudiante"
    invitado = "invitado"

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(Enum(RoleEnum), default=RoleEnum.estudiante)
    avatar = Column(String(255), nullable=True, default="default_avatar.png")
    nivel = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    monedas = Column(Integer, default=0)
    vidas = Column(Integer, default=5)
    racha = Column(Integer, default=0)
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)

    progreso = relationship("Progress", back_populates="usuario")
    monstruo = relationship("Monster", back_populates="usuario", uselist=False)

class Exercise(Base):
    __tablename__ = "ejercicios"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    ejemplo_codigo = Column(Text, nullable=True)
    respuesta_correcta = Column(Text, nullable=False)
    xp_recompensa = Column(Integer, default=10)
    nivel_requerido = Column(Integer, default=1)

    progreso = relationship("Progress", back_populates="ejercicio")

class Progress(Base):
    __tablename__ = "progreso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    ejercicio_id = Column(Integer, ForeignKey("ejercicios.id"))
    completado = Column(Boolean, default=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)

    usuario = relationship("User", back_populates="progreso")
    ejercicio = relationship("Exercise", back_populates="progreso")

class Achievement(Base):
    __tablename__ = "logros"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    icono = Column(String(255), nullable=True)
    recompensa_xp = Column(Integer, default=20)

class Monster(Base):
    __tablename__ = "monstruos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    ojos = Column(String(100), default="normal")
    boca = Column(String(100), default="sonrisa")
    color = Column(String(100), default="azul")
    accesorio = Column(String(100), nullable=True)

    usuario = relationship("User", back_populates="monstruo")

class Reward(Base):
    __tablename__ = "recompensas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    monedas = Column(Integer, default=10)


class MonsterItem(Base):
    """Partes del monstruo que el usuario compró con sus monedas."""
    __tablename__ = "monstruo_items"
    __table_args__ = (UniqueConstraint("usuario_id", "item_id", name="uq_usuario_item"),)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    item_id = Column(String(50), nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)

class MemoryGame(Base):
    """Partidas completadas del juego de memoria (Partida_Memoria)."""
    __tablename__ = "partidas_memoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    movimientos = Column(Integer, default=0)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
