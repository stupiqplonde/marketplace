# repositories.py
import json
from typing import List, Optional, Dict, Any
import uuid


# Импорты моделей будут в конце файла, чтобы избежать циклических импортов

class BaseRepository:
    def __init__(self, db, table_name: str):
        self.db = db
        self.table_name = table_name


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "users")

    def create(self, user):
        from models import User, UserRole
        query = """
        INSERT INTO users (user_id, email, password_hash, role, first_name, last_name, avatar_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_command(query, (
            str(user.user_id), user.email, user.password_hash, user.role.value,
            user.first_name, user.last_name, user.avatar_url
        ))
        return user

    def get_by_id(self, user_id: uuid.UUID):
        from models import User, UserRole
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.db.execute_query(query, (str(user_id),))
        if result:
            return self._map_to_user(result[0])
        return None

    def get_by_email(self, email: str):
        from models import User, UserRole
        query = "SELECT * FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,))
        if result:
            return self._map_to_user(result[0])
        return None

    def _map_to_user(self, data):
        from models import User, UserRole
        return User(
            user_id=uuid.UUID(data['user_id']),
            email=data['email'],
            password_hash=data['password_hash'],
            role=UserRole(data['role']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            avatar_url=data['avatar_url'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )


class ProductRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "products")

    def create(self, product):
        from models import Product, ProductStatus
        query = """
        INSERT INTO products (product_id, seller_id, category_id, name, description, 
                             price, currency, stock_quantity, sku, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_command(query, (
            str(product.product_id), str(product.seller_id), product.category_id, product.name,
            product.description, product.price, product.currency, product.stock_quantity,
            product.sku, product.status.value
        ))
        return product

    def get_by_id(self, product_id: uuid.UUID):
        from models import Product, ProductStatus
        query = "SELECT * FROM products WHERE product_id = ?"
        result = self.db.execute_query(query, (str(product_id),))
        if result:
            return self._map_to_product(result[0])
        return None

    def get_by_category(self, category_id: int, status=None):
        from models import Product, ProductStatus
        if status:
            query = "SELECT * FROM products WHERE category_id = ? AND status = ?"
            result = self.db.execute_query(query, (category_id, status.value))
        else:
            query = "SELECT * FROM products WHERE category_id = ?"
            result = self.db.execute_query(query, (category_id,))

        return [self._map_to_product(row) for row in result]

    def update_stock(self, product_id: uuid.UUID, new_quantity: int) -> None:
        query = "UPDATE products SET stock_quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?"
        self.db.execute_command(query, (new_quantity, str(product_id)))

    def _map_to_product(self, data):
        from models import Product, ProductStatus
        return Product(
            product_id=uuid.UUID(data['product_id']),
            seller_id=uuid.UUID(data['seller_id']),
            category_id=data['category_id'],
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            currency=data['currency'],
            stock_quantity=data['stock_quantity'],
            sku=data['sku'],
            status=ProductStatus(data['status']),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )


class OrderRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "orders")

    def create(self, order):
        from models import Order, OrderStatus
        query = """
        INSERT INTO orders (order_id, buyer_id, status, total_amount, shipping_address, billing_address)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.execute_command(query, (
            str(order.order_id), str(order.buyer_id), order.status.value, order.total_amount,
            json.dumps(order.shipping_address), json.dumps(order.billing_address)
        ))
        return order

    def add_order_item(self, order_item):
        from models import OrderItem
        query = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)
        """
        self.db.execute_command(query, (
            str(order_item.order_id), str(order_item.product_id), order_item.quantity, order_item.unit_price
        ))
        # Получаем ID последней вставленной записи
        result = self.db.execute_query("SELECT last_insert_rowid() as id")
        order_item.order_item_id = result[0]['id']
        return order_item

    def get_by_buyer(self, buyer_id: uuid.UUID):
        from models import Order, OrderStatus
        query = "SELECT * FROM orders WHERE buyer_id = ? ORDER BY created_at DESC"
        result = self.db.execute_query(query, (str(buyer_id),))
        return [self._map_to_order(row) for row in result]

    def _map_to_order(self, data):
        from models import Order, OrderStatus
        return Order(
            order_id=uuid.UUID(data['order_id']),
            buyer_id=uuid.UUID(data['buyer_id']),
            status=OrderStatus(data['status']),
            total_amount=float(data['total_amount']),
            shipping_address=json.loads(data['shipping_address']),
            billing_address=json.loads(data['billing_address']),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )


class CategoryRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "categories")

    def create(self, name: str, slug: str, description: str = ""):
        from models import Category
        query = """
        INSERT INTO categories (name, slug, description) 
        VALUES (?, ?, ?)
        """
        self.db.execute_command(query, (name, slug, description))

        # Получаем ID последней вставленной записи
        result = self.db.execute_query("SELECT last_insert_rowid() as id")
        category_id = result[0]['id']

        return Category(
            category_id=category_id,
            name=name,
            slug=slug,
            description=description
        )

    def get_all(self):
        from models import Category
        query = "SELECT * FROM categories"
        result = self.db.execute_query(query)
        return [Category(
            category_id=row['category_id'],
            name=row['name'],
            description=row['description'],
            slug=row['slug'],
            created_at=row['created_at']
        ) for row in result]