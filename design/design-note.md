# Design Note — REST Product Service

## Scope
A standalone Product Service for an online store. Other services can call its versioned REST API later.

## Data model
`products`: auto-increment integer `id`; `name` (2–100, unique case-insensitively); optional `description` (max 500); positive decimal `price` (2 decimal places); nonnegative integer `quantity`; `category` (2–50); `status` (`ACTIVE`/`INACTIVE`, default `ACTIVE`); server-managed `created_at` and `updated_at`.

## Endpoints
- `POST /api/v1/products` — create, 201 and Location header
- `GET /api/v1/products/{id}` — retrieve one, 200
- `GET /api/v1/products` — paginated/filterable/sortable list, 200
- `PUT /api/v1/products/{id}` — full replacement, 200
- `PATCH /api/v1/products/{id}` — partial update, 200
- `DELETE /api/v1/products/{id}` — delete, 204
- `GET /health` — API/database health, 200

## Validation and errors
Trim text; reject invalid types, missing required fields, bad ranges, malformed IDs and unknown fields in input DTOs. Duplicate names return 409; missing records 404; validation errors 400. Errors use `timestamp`, `status`, `error`, `message`, `path`, and `details`.

## Architecture
FastAPI router/controller handles HTTP and DTOs; service owns business rules; repository owns SQL queries and persistence; SQLAlchemy model maps to MySQL. Alembic applies schema migrations. Environment variables configure connection settings. Pytest exercises API behaviour.
