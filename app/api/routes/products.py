from decimal import Decimal
from typing import Annotated
from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.products.models import ProductStatus
from app.products.schemas import ProductCreate, ProductOut, ProductPatch, ProductPage, ProductReplace
from app.products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

def parse_sort(sort: str):
    parts = [p.strip() for p in sort.split(",")]
    if len(parts) != 2 or parts[0] not in {"price", "name", "quantity", "created_at", "updated_at"} or parts[1].lower() not in {"asc", "desc"}:
        from app.core.errors import AppError
        raise AppError(400, "Bad Request", "Invalid sort value",
                       [{"field": "sort", "issue": "use field,asc|desc (e.g. price,asc)"}])
    return parts[0], parts[1].lower()

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, response: Response, db: Session = Depends(get_db)):
    product = ProductService(db).create(payload.model_dump())
    response.headers["Location"] = f"/api/v1/products/{product.id}"
    return product

@router.get("", response_model=ProductPage)
def list_products(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    category: str | None = Query(None, min_length=2, max_length=50),
    status_filter: ProductStatus | None = Query(None, alias="status"),
    min_price: Decimal | None = Query(None, gt=0, alias="minPrice"),
    max_price: Decimal | None = Query(None, gt=0, alias="maxPrice"),
    sort: str = Query("created_at,desc"),
    db: Session = Depends(get_db),
):
    return ProductService(db).list(page, size, category.strip() if category else None,
                                   status_filter, min_price, max_price, parse_sort(sort))

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService(db).get(product_id)

@router.put("/{product_id}", response_model=ProductOut)
def replace_product(product_id: int, payload: ProductReplace, db: Session = Depends(get_db)):
    return ProductService(db).replace(product_id, payload.model_dump())

@router.patch("/{product_id}", response_model=ProductOut)
def patch_product(product_id: int, payload: ProductPatch, db: Session = Depends(get_db)):
    return ProductService(db).patch(product_id, payload.model_dump(exclude_unset=True))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    ProductService(db).delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
