from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.products.models import ProductStatus

def trim_text(value):
    if isinstance(value, str):
        return value.strip()
    return value

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)
    category: str = Field(min_length=2, max_length=50)
    status: ProductStatus = ProductStatus.ACTIVE

    @field_validator("name", "description", "category", mode="before")
    @classmethod
    def trim_fields(cls, value):
        return trim_text(value)

    @field_validator("name", "category")
    @classmethod
    def not_blank(cls, value):
        if not value or not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("description")
    @classmethod
    def description_trimmed(cls, value):
        return value if value != "" else None

class ProductReplace(ProductCreate):
    pass

class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    status: ProductStatus | None = None

    @field_validator("name", "description", "category", mode="before")
    @classmethod
    def trim_fields(cls, value):
        return trim_text(value)

    @field_validator("name", "category")
    @classmethod
    def not_blank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("provide at least one field to update")
        return self

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    quantity: int
    category: str
    status: ProductStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductPage(BaseModel):
    items: list[ProductOut]
    page: int
    size: int
    totalItems: int
    totalPages: int
