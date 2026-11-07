import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.auth import get_current_user

router = APIRouter()

# ---------- Catálogo de la tienda del monstruo ----------
def _item(tipo, valor, nombre, precio):
    return {"id": f"{tipo}:{valor}", "tipo": tipo, "valor": valor, "nombre": nombre, "precio": precio}

CATALOG = [
    _item("color", "azul", "Azul", 0), _item("color", "verde", "Verde", 10),
    _item("color", "rosa", "Rosa", 10), _item("color", "naranja", "Naranja", 10),
    _item("ojos", "normal", "Normales", 0), _item("ojos", "grandes", "Grandes", 10),
    _item("ojos", "estrellas", "Estrellas", 20),
    _item("boca", "sonrisa", "Sonrisa", 0), _item("boca", "risa", "Risa", 10),
    _item("boca", "sorpresa", "Sorpresa", 15),
    _item("accesorio", "ninguno", "Ninguno", 0), _item("accesorio", "gorra", "Gorra", 15),
    _item("accesorio", "lentes", "Lentes", 15), _item("accesorio", "corona", "Corona", 30),
]
CATALOG_BY_ID = {i["id"]: i for i in CATALOG}
SLOTS = ("ojos", "boca", "color", "accesorio")
DEFAULTS = {"ojos": "normal", "boca": "sonrisa", "color": "azul", "accesorio": "ninguno"}

def _monster(db: Session, user: models.User) -> models.Monster:
    m = db.query(models.Monster).filter(models.Monster.usuario_id == user.id).first()
    if not m:
        m = models.Monster(usuario_id=user.id, **DEFAULTS)
        db.add(m); db.commit(); db.refresh(m)
    return m

def _state(db: Session, user: models.User):
    m = _monster(db, user)
    owned = [r.item_id for r in db.query(models.MonsterItem).filter(models.MonsterItem.usuario_id == user.id)]
    return {
        "monster": {s: (getattr(m, s) or DEFAULTS[s]) for s in SLOTS},
        "owned": owned, "catalog": CATALOG, "monedas": user.monedas,
    }

def _owns(item, owned):
    return item["precio"] == 0 or item["id"] in owned

@router.get("/status/{user_id}")
def get_gamification_status(user_id: int, user: models.User = Depends(get_current_user)):
    if user.id != user_id and user.rol.value not in ("admin", "docente"):
        raise HTTPException(status_code=403, detail="No autorizado")
    return {"nivel": user.nivel, "xp": user.xp, "monedas": user.monedas, "vidas": user.vidas, "racha": user.racha}

# ---------- Mi Monstruo ----------
@router.get("/monster")
def get_monster(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return _state(db, user)

class BuyItem(BaseModel):
    item_id: str

@router.post("/monster/buy")
def buy_item(data: BuyItem, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    item = CATALOG_BY_ID.get(data.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ese objeto no existe")
    owned = _state(db, user)["owned"]
    if not _owns(item, owned):
        if user.monedas < item["precio"]:
            raise HTTPException(status_code=400, detail="Aún no tienes monedas suficientes 🪙")
        user.monedas -= item["precio"]
        db.add(models.MonsterItem(usuario_id=user.id, item_id=item["id"]))
        db.commit()
    return _state(db, user)

@router.put("/monster")
def save_monster(data: schemas.MonsterUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    owned = _state(db, user)["owned"]
    m = _monster(db, user)
    for slot, valor in data.dict(exclude_unset=True).items():
        if valor is None:
            continue
        item = CATALOG_BY_ID.get(f"{slot}:{valor}")
        if not item or not _owns(item, owned):
            raise HTTPException(status_code=403, detail="Primero debes comprar ese objeto")
        setattr(m, slot, valor)
    db.commit()
    return _state(db, user)

# ---------- Juego de memoria ----------
class MemoryResult(BaseModel):
    movimientos: int

MAX_REWARDED_GAMES_PER_DAY = 3

@router.post("/memory")
def memory_completed(data: MemoryResult, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    start = datetime.datetime.combine(datetime.datetime.utcnow().date(), datetime.time.min)
    today = db.query(models.MemoryGame).filter(
        models.MemoryGame.usuario_id == user.id, models.MemoryGame.fecha >= start).count()
    db.add(models.MemoryGame(usuario_id=user.id, movimientos=max(0, data.movimientos)))
    ganadas = 0
    if today < MAX_REWARDED_GAMES_PER_DAY:
        ganadas = 5
        user.monedas += ganadas
        user.xp += 10
        while user.xp >= user.nivel * 100:
            user.nivel += 1
    db.commit()
    return {"monedas_ganadas": ganadas, "monedas": user.monedas, "partidas_hoy": today + 1}
