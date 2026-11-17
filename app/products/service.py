from math import ceil
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.products.models import ProductStatus
from app.products.repository import ProductRepository

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def _ensure_unique_name(self, name: str, exclude_id: int | None = None):
        existing = self.repo.get_by_name_ci(name)
        if existing and existing.id != exclude_id:
            raise AppError(409, "Conflict", "A product with this name already exists",
                           [{"field": "name", "issue": "must be unique (case-insensitive)"}])

    def create(self, data: dict):
        self._ensure_unique_name(data["name"])
        try:
            return self.repo.create(data)
        except IntegrityError:
            self.repo.db.rollback()
            raise AppError(409, "Conflict", "A product with this name already exists")

    def get(self, product_id: int):
        product = self.repo.get(product_id)
        if not product:
            raise AppError(404, "Not Found", f"Product {product_id} was not found")
        return product

    def list(self, page, size, category, status, min_price, max_price, sort):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise AppError(400, "Bad Request", "minPrice must be less than or equal to maxPrice",
                           [{"field": "minPrice", "issue": "must be <= maxPrice"}])
        sort_field, sort_dir = sort
        items, total = self.repo.list(page, size, category, status, min_price, max_price, sort_field, sort_dir)
        return {"items": items, "page": page, "size": size, "totalItems": total,
                "totalPages": ceil(total / size) if total else 0}

    def replace(self, product_id: int, data: dict):
        product = self.get(product_id)
        self._ensure_unique_name(data["name"], product_id)
        for key, value in data.items():
            setattr(product, key, value)
        try:
            return self.repo.save(product)
        except IntegrityError:
            self.repo.db.rollback()
            raise AppError(409, "Conflict", "A product with this name already exists")

    def patch(self, product_id: int, data: dict):
        product = self.get(product_id)
        changes = data
        if "name" in changes and changes["name"] is not None:
            self._ensure_unique_name(changes["name"], product_id)
        for key, value in changes.items():
            setattr(product, key, value)
        try:
            return self.repo.save(product)
        except IntegrityError:
            self.repo.db.rollback()
            raise AppError(409, "Conflict", "A product with this name already exists")

    def delete(self, product_id: int):
        product = self.get(product_id)
        self.repo.delete(product)
