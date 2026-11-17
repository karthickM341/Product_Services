import logging
import time
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.products import router as products_router
from app.core.config import settings
from app.core.errors import AppError
from app.api.routes.health import router as health_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("product_service")

app = FastAPI(title="Product Service", version="1.0.0",
              description="Layered REST Product Service backed by MySQL. See README for migration instructions.")

@app.middleware("http")
async def request_logging(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("%s %s -> %s (%.2f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
        return response
    except Exception:
        logger.exception("Unhandled request error: %s %s", request.method, request.url.path)
        raise

def error_payload(request: Request, status: int, error: str, message: str, details=None):
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "error": error,
        "message": message,
        "path": request.url.path,
        "details": details or [],
    }

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code,
        content=error_payload(request, exc.status_code, exc.error, exc.message, exc.details))

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []
    for item in exc.errors():
        loc = item.get("loc", [])
        field = ".".join(str(part) for part in loc if part not in ("body", "query", "path")) or "request"
        details.append({"field": field, "issue": item.get("msg", "invalid value")})
    return JSONResponse(status_code=400,
        content=error_payload(request, 400, "Bad Request", "Validation failed", details))

@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    labels = {404: "Not Found", 405: "Method Not Allowed"}
    return JSONResponse(status_code=exc.status_code,
        content=error_payload(request, exc.status_code, labels.get(exc.status_code, "HTTP Error"),
                              str(exc.detail), []))

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("Database integrity error on %s", request.url.path)
    return JSONResponse(status_code=409,
        content=error_payload(request, 409, "Conflict", "A product with this name already exists", []))

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unexpected server error")
    return JSONResponse(status_code=500,
        content=error_payload(request, 500, "Internal Server Error", "An unexpected error occurred", []))

app.include_router(products_router, prefix="/api/v1")
app.include_router(health_router)

@app.get("/", include_in_schema=False)
def root():
    return {"service": settings.APP_NAME, "docs": "/docs", "health": "/health"}
