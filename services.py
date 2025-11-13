# services.py
from typing import List, Optional, Dict, Any
import uuid


class ProductService:
    def __init__(self, product_repo):
        self.product_repo = product_repo

    def create_product(self, seller_id: uuid.UUID, category_id: int, name: str,
                       description: str, price: float, stock_quantity: int = 0):
        from models import Product, ProductStatus
        product = Product(
            seller_id=seller_id,
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            status=ProductStatus.UNDER_MODERATION
        )
        return self.product_repo.create(product)

    def get_available_products(self, category_id: Optional[int] = None):
        from models import ProductStatus
        if category_id:
            return self.product_repo.get_by_category(category_id, ProductStatus.ACTIVE)
        else:
            # Здесь можно добавить логику для получения всех доступных товаров
            return []


class OrderService:
    def __init__(self, order_repo, product_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def create_order(self, buyer_id: uuid.UUID, items: List[Dict],
                     shipping_address: Dict, billing_address: Dict):
        from models import Order, OrderStatus, OrderItem
        try:
            # Проверка доступности товаров и расчет общей суммы
            total_amount = 0.0
            order_items = []

            for item in items:
                product = self.product_repo.get_by_id(item['product_id'])
                if not product or product.stock_quantity < item['quantity']:
                    raise ValueError(f"Product {item['product_id']} is not available")

                total_amount += product.price * item['quantity']
                order_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'unit_price': product.price
                })

            # Создание заказа
            order = Order(
                buyer_id=buyer_id,
                total_amount=total_amount,
                shipping_address=shipping_address,
                billing_address=billing_address,
                status=OrderStatus.PENDING
            )
            order = self.order_repo.create(order)

            # Добавление позиций заказа
            for item_data in order_items:
                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=item_data['product'].product_id,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                self.order_repo.add_order_item(order_item)

                # Обновление остатков
                new_quantity = item_data['product'].stock_quantity - item_data['quantity']
                self.product_repo.update_stock(item_data['product'].product_id, new_quantity)

            return order

        except Exception as e:
            print(f"Order creation failed: {e}")
            return None


class MarketplaceService:
    def __init__(self, db):
        from repositories import UserRepository, ProductRepository, OrderRepository, CategoryRepository
        self.db = db
        self.user_repo = UserRepository(db)
        self.product_repo = ProductRepository(db)
        self.order_repo = OrderRepository(db)
        self.category_repo = CategoryRepository(db)
        self.product_service = ProductService(self.product_repo)
        self.order_service = OrderService(self.order_repo, self.product_repo)

    def register_user(self, email: str, password_hash: str, first_name: str,
                      last_name: str, role=None):
        from models import User, UserRole
        if role is None:
            role = UserRole.BUYER

        if self.user_repo.get_by_email(email):
            raise ValueError("User with this email already exists")

        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        return self.user_repo.create(user)

    def get_categories(self):
        """Получить все категории"""
        return self.category_repo.get_all()