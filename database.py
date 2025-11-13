# database.py
import sqlite3
import os
from typing import List, Dict, Any, Optional


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseManager(metaclass=Singleton):
    def __init__(self, db_path: str = "marketplace.db"):
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._initialize_database()

    def _connect(self):
        """Установка соединения с SQLite"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
            print("✅ SQLite connection established")
        except Exception as e:
            print(f"❌ SQLite connection failed: {e}")
            raise

    def _initialize_database(self):
        """Инициализация структуры базы данных"""
        try:
            with self.connection:
                self.connection.executescript(self._get_schema_sql())
            print("✅ Database schema initialized")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

    def _get_schema_sql(self) -> str:
        """SQL скрипт для создания таблиц"""
        return """
        -- Пользователи
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('buyer', 'seller', 'admin')),
            first_name TEXT,
            last_name TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Продавцы (расширение пользователей)
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id TEXT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
            company_name TEXT,
            description TEXT,
            tax_id TEXT,
            bank_details TEXT,
            rating_avg REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Категории
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            parent_category_id INTEGER REFERENCES categories(category_id),
            slug TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Товары
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            seller_id TEXT NOT NULL REFERENCES sellers(seller_id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(category_id),
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL CHECK (price >= 0),
            currency TEXT DEFAULT 'USD',
            stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
            sku TEXT,
            status TEXT DEFAULT 'under_moderation' 
                CHECK (status IN ('active', 'inactive', 'under_moderation', 'out_of_stock')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Атрибуты товаров
        CREATE TABLE IF NOT EXISTS product_attributes (
            product_id TEXT REFERENCES products(product_id) ON DELETE CASCADE,
            attribute_key TEXT NOT NULL,
            attribute_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (product_id, attribute_key)
        );

        -- Изображения товаров
        CREATE TABLE IF NOT EXISTS product_images (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
            image_url TEXT NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Заказы
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            buyer_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            status TEXT DEFAULT 'pending'
                CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')),
            total_amount REAL NOT NULL CHECK (total_amount >= 0),
            shipping_address TEXT NOT NULL,
            billing_address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Позиции заказа
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
            product_id TEXT NOT NULL REFERENCES products(product_id),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Платежи
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
            payment_method TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount >= 0),
            status TEXT DEFAULT 'pending'
                CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
            transaction_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Отзывы
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
            buyer_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id, buyer_id, order_id)
        );
        """

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Выполнение SELECT запроса"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            raise

    def execute_command(self, command: str, params: tuple = None) -> None:
        """Выполнение INSERT/UPDATE/DELETE команды"""
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(command, params or ())
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            raise

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")