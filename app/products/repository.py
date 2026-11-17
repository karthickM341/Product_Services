from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.products.models import Product, ProductStatus

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int):
        return self.db.get(Product, product_id)

    def get_by_name_ci(self, name: str):
        return self.db.scalar(select(Product).where(func.lower(Product.name) == name.lower()))

    def create(self, values: dict):
        product = Product(**values)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save(self, product: Product):
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product):
        self.db.delete(product)
        self.db.commit()

    def list(self, page, size, category, status, min_price, max_price, sort_field, sort_dir):
        query = select(Product)
        count_query = select(func.count()).select_from(Product)
        filters = []
        if category:
            filters.append(func.lower(Product.category) == category.lower())
        if status:
            filters.append(Product.status == status)
        if min_price is not None:
            filters.append(Product.price >= min_price)
        if max_price is not None:
            filters.append(Product.price <= max_price)
        for condition in filters:
            query = query.where(condition)
            count_query = count_query.where(condition)
        column = getattr(Product, sort_field)
        query = query.order_by(column.asc() if sort_dir == "asc" else column.desc())
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.offset(page * size).limit(size)).all())
        return items, total
