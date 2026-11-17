# Product Service 

A foundational REST Product Service for an online store, implemented with Python 3.12, FastAPI, SQLAlchemy 2, MySQL 8 and Alembic. It follows controller/router → service → repository → database layering and uses response DTOs rather than returning ORM entities directly.

## Features
- Create, retrieve, list, replace, partially update and delete products
- MySQL persistence and explicit Alembic migration
- Case-insensitive duplicate-name checks
- Validation, trimmed text fields, consistent JSON error format
- Pagination (zero-based `page`), filtering, sorting and metadata
- Health check, request/error logging, Swagger/OpenAPI
- Pytest unit/API tests; tests use isolated in-memory SQLite only, while the app uses MySQL

## Prerequisites
- Python 3.12+
- MySQL 8.0+ 
- Git (recommended)

## Run locally on Windows PowerShell

1. Create a MySQL database and user (run in MySQL Workbench as an administrator):

```sql
CREATE DATABASE product_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'product_user'@'localhost' IDENTIFIED BY 'choose_a_strong_password';
GRANT ALL PRIVILEGES ON product_service.* TO 'product_user'@'localhost';
FLUSH PRIVILEGES;
```

2. From this project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Edit `.env` and set `DB_PASSWORD` to the password you chose. Do not commit `.env`.

4. Apply the schema migration, then start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Open Swagger UI at http://127.0.0.1:8000/docs and health check at http://127.0.0.1:8000/health.

## Run with Docker

Docker Compose starts MySQL, waits for its health check, applies the migration and starts the API:

```powershell
docker compose up --build
```

For local learning only, the compose file contains example credentials. Change them before using outside a local development machine. Stop with `Ctrl+C`; use `docker compose down` to stop containers. `docker compose down -v` also deletes the local database volume.

## Endpoints

Base path: `/api/v1/products`

| Method | Path | Purpose | Success |
|---|---|---|---|
| POST | `/api/v1/products` | Create | 201 + `Location` |
| GET | `/api/v1/products/{id}` | Get one | 200 |
| GET | `/api/v1/products` | List | 200 |
| PUT | `/api/v1/products/{id}` | Full replacement | 200 |
| PATCH | `/api/v1/products/{id}` | Partial update | 200 |
| DELETE | `/api/v1/products/{id}` | Delete | 204 |
| GET | `/health` | Database/API health | 200 |

List query parameters:
- `page`: zero-based, default `0`
- `size`: default `10`, range `1..100`
- `category`: exact case-insensitive category
- `status`: `ACTIVE` or `INACTIVE`
- `minPrice`, `maxPrice`
- `sort`: `price,asc`, `name,desc`, `quantity,asc`, `created_at,desc`, etc.

Example request:

```json
{
  "name": "Desk Lamp",
  "description": "LED desk lamp",
  "price": "25.50",
  "quantity": 12,
  "category": "Lighting",
  "status": "ACTIVE"
}
```

Example list: `GET /api/v1/products?page=0&size=10&category=Lighting&minPrice=10&maxPrice=100&sort=price,asc`

Every error response follows this shape:

```json
{
  "timestamp": "2026-10-27T10:15:30Z",
  "status": 404,
  "error": "Not Found",
  "message": "Product 123 was not found",
  "path": "/api/v1/products/123",
  "details": []
}
```

## Tests and coverage

```powershell
pytest -q
pytest --cov=app.products.service --cov-report=term-missing
```

The provided tests cover create/get, validation, duplicate names, not found, list/pagination/sorting, PUT/PATCH/DELETE and health. Check the coverage output locally and add cases until the mentor's 70% service-layer target is met; do not assume the target is met without running the report.

## Project structure

```text
app/
  api/routes/       # HTTP endpoints
  core/             # settings and application errors
  db/               # SQLAlchemy base and session
  products/         # model, DTO schemas, repository, business service
alembic/
  versions/         # explicit schema migration
tests/              # API/integration tests
postman/             # sample requests
design/              # one-page design note
```

## Notes
- `id`, `created_at`, and `updated_at` are server-managed and ignored/rejected by the input DTOs.
- Product deletion is hard delete to match the required 204 endpoint; soft delete can be added as a stretch goal.
- The MySQL unique index protects exact duplicates; the service additionally checks names case-insensitively. For high-concurrency production workloads, consider a database-level normalized-name column/index to enforce case-insensitive uniqueness atomically under the selected MySQL collation.
- The error handler intentionally avoids exposing exception internals.
