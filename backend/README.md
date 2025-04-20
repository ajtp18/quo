# Banking API

API REST para gestión bancaria construida con FastAPI y PostgreSQL.

## Características

- Autenticación JWT con tokens de acceso y refresco
- Integración con Belvo para conexión bancaria
- Cache con Redis
- Base de datos PostgreSQL con SQLAlchemy
- Migraciones con Alembic

## Requisitos

- Python 3.9+
- PostgreSQL
- Redis

## Configuración

1. Crear archivo `.env` en la raíz:

```bash
DATABASE_URL="postgresql://user:password@host:port/database"
JWT_SECRET="tu_clave_secreta"
JWT_REFRESH_SECRET="tu_clave_secreta_refresco"
REDIS_URL="redis://localhost:6379"
```

2. Instalar dependencias:

```bash
poetry install
```

3. Ejecutar migraciones:

```bash
poetry run alembic upgrade head
```

4. Ejecutar servidor:

```bash
poetry run uvicorn app.main:app --reload
```

## Documentación

Documentación interactiva con Swagger:

```bash
http://localhost:8000/docs
```

## Migraciones

Crear nueva migración:

```bash
poetry run alembic revision --autogenerate -m "Descripción de la migración"
```

Aplicar migraciones:

```bash
poetry run alembic upgrade head
```
