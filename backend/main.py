import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, users, exercises, gamification

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pycods API",
    description="API robusta para la plataforma educativa inclusiva Pycods (TEA)",
    version="2.0.0"
)

# Orígenes permitidos (frontend en 4042; 4200 por si usas `ng serve`)
origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4042,http://127.0.0.1:4042,http://localhost:4200",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["Ejercicios y Progreso"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["Gamificación y Monstruo"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Pycods - Inclusión + Tecnología + Diversión"}


@app.get("/health")
def health():
    return {"status": "ok"}
