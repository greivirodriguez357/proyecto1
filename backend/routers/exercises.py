from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from routers.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.ExerciseResponse])
def get_exercises(db: Session = Depends(get_db)):
    exercises = db.query(models.Exercise).all()
    if not exercises:
        # Initial seed if empty
        default_exercises = [
            models.Exercise(titulo="1. Variables y Mensajes", descripcion="Guarda datos en una variable y muéstrala.", ejemplo_codigo='nombre = "Samuel"\nprint(nombre)', respuesta_correcta='Samuel', xp_recompensa=20, nivel_requerido=1),
            models.Exercise(titulo="2. Condicionales if/else", descripcion="Toma decisiones en Python.", ejemplo_codigo='edad = 10\nif edad >= 10:\n    print("¡Puedes jugar!")', respuesta_correcta='¡Puedes jugar!', xp_recompensa=30, nivel_requerido=1),
            models.Exercise(titulo="3. Bucles for", descripcion="Repite acciones en secuencia.", ejemplo_codigo='for i in range(3):\n    print("Hola")', respuesta_correcta='Hola\nHola\nHola', xp_recompensa=40, nivel_requerido=2)
        ]
        db.add_all(default_exercises)
        db.commit()
        exercises = db.query(models.Exercise).all()
    return exercises

@router.post("/", response_model=schemas.ExerciseResponse)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = models.Exercise(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.get("/progress/{user_id}", response_model=List[int])
def get_completed(user_id: int, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    """IDs de ejercicios completados por el usuario."""
    if current_user.id != user_id and current_user.rol.value not in ("admin", "docente"):
        raise HTTPException(status_code=403, detail="No autorizado")
    rows = (db.query(models.Progress.ejercicio_id)
              .filter(models.Progress.usuario_id == user_id, models.Progress.completado == True)  # noqa: E712
              .distinct().all())
    return [r[0] for r in rows]

@router.post("/progress/{user_id}")
def submit_progress(user_id: int, progress_data: schemas.ProgressCreate, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes registrar tu propio progreso")
    user = current_user
    exercise = db.query(models.Exercise).filter(models.Exercise.id == progress_data.ejercicio_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    already = db.query(models.Progress).filter(
        models.Progress.usuario_id == user_id,
        models.Progress.ejercicio_id == exercise.id,
        models.Progress.completado == True,  # noqa: E712
    ).first()

    if progress_data.completado and not already:
        db.add(models.Progress(usuario_id=user_id, ejercicio_id=exercise.id, completado=True))
        user.xp += exercise.xp_recompensa
        user.monedas += 5
        while user.xp >= user.nivel * 100:
            user.nivel += 1
        db.commit()
        return {"message": "Progreso actualizado con éxito", "xp_ganado": exercise.xp_recompensa,
                "xp_actual": user.xp, "nivel_actual": user.nivel, "monedas": user.monedas}

    return {"message": "Ejercicio ya completado antes (sin XP extra)" if already else "Intento registrado",
            "xp_ganado": 0, "xp_actual": user.xp, "nivel_actual": user.nivel, "monedas": user.monedas}
