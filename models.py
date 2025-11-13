# models.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from enum import Enum

class UserRole(Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_MODERATION = "under_moderation"
    OUT_OF_STOCK = "out_of_stock"

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class User:
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.BUYER
    first_name: str = ""
    last_name: str = ""
    avatar_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Seller:
    seller_id: uuid.UUID = field(default_factory=uuid.uuid4)
    company_name: str = ""
    description: str = ""
    tax_id: str = ""
    bank_details: Dict[str, Any] = field(default_factory=dict)
    rating_avg: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Category:
    category_id: int = 0
    name: str = ""
    description: str = ""
    parent_category_id: Optional[int] = None
    slug: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Product:
    product_id: uuid.UUID = field(default_factory=uuid.uuid4)
    seller_id: uuid.UUID = field(default_factory=uuid.uuid4)
    category_id: int = 0
    name: str = ""
    description: str = ""
    price: float = 0.0
    currency: str = "USD"
    stock_quantity: int = 0
    sku: str = ""
    status: ProductStatus = ProductStatus.UNDER_MODERATION
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProductAttribute:
    product_id: uuid.UUID = field(default_factory=uuid.uuid4)
    attribute_key: str = ""
    attribute_value: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Order:
    order_id: uuid.UUID = field(default_factory=uuid.uuid4)
    buyer_id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float = 0.0
    shipping_address: Dict[str, Any] = field(default_factory=dict)
    billing_address: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class OrderItem:
    order_item_id: int = 0
    order_id: uuid.UUID = field(default_factory=uuid.uuid4)
    product_id: uuid.UUID = field(default_factory=uuid.uuid4)
    quantity: int = 0
    unit_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)