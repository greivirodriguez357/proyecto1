# Pycods - Plataforma Educativa Inclusiva (Full-Stack Integrada)

**Pycods** es una aplicación interactiva y gamificada orientada al aprendizaje del lenguaje de programación Python para niños con Trastorno del Espectro Autista (TEA).

## Arquitectura Integrada
- **Backend:** FastAPI, SQLAlchemy 2.0, PostgreSQL 15, Pydantic v2, JWT (bcrypt).
- **Frontend:** Angular 17, PrimeNG, AG Grid Community, PrimeFlex (Metodología TEACCH / Accesibilidad sensorial).
- **Orquestación:** Docker Compose (Base de datos PostgreSQL + API REST + Nginx Frontend).

## Instrucciones de Despliegue Automatizado (Docker)

1. Asegúrate de tener instalado **Docker** y **Docker Compose**.
2. En la raíz del proyecto, ejecuta:
   ```bash
   docker-compose up --build
   ```
3. Puertos de acceso:
   - **Frontend (Angular app):** `http://localhost:4042`
   - **Backend API REST:** `http://localhost:8001`
   - **Documentación Swagger / OpenAPI:** `http://localhost:8001/docs`

## Ejecución Local en Desarrollo (Sin Docker)

### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # O venv\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend:
```bash
cd frontend
npm install
npm start   # ng serve en http://localhost:4042 (proxy /api -> localhost:8001)
```
