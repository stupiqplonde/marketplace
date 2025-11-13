import os
import sys
from datetime import datetime
from database import SQLiteManager
from services import MarketplaceService
from models import UserRole, ProductStatus
import uuid


def setup_initial_data(marketplace):
    """Начальная настройка тестовых данных"""
    print("🔄 Настройка начальных данных...")

    # Регистрация пользователей
    try:
        buyer = marketplace.register_user(
            email="buyer@example.com",
            password_hash="hashed_password_123",
            first_name="Иван",
            last_name="Петров",
            role=UserRole.BUYER
        )
        print(f"✅ Покупатель зарегистрирован: {buyer.first_name} {buyer.last_name}")

        seller = marketplace.register_user(
            email="seller@example.com",
            password_hash="hashed_password_456",
            first_name="Анна",
            last_name="Сидорова",
            role=UserRole.SELLER
        )
        print(f"✅ Продавец зарегистрирован: {seller.first_name} {seller.last_name}")

        # Создание тестовых категорий
        categories = [
            ("Электроника", "electronics", "Смартфоны, ноутбуки, планшеты"),
            ("Одежда", "clothing", "Одежда и аксессуары"),
            ("Книги", "books", "Художественная и учебная литература")
        ]

        for name, slug, desc in categories:
            marketplace.category_repo.create(name, slug, desc)
        print("✅ Тестовые категории созданы")

        return buyer, seller

    except Exception as e:
        print(f"❌ Ошибка при настройке данных: {e}")
        return None, None


def demo_scenario(marketplace, buyer, seller):
    """Демонстрационный сценарий работы маркетплейса"""
    print("\n🎬 Запуск демонстрационного сценария...")

    try:
        # Создание товаров
        products = [
            ("iPhone 13", "Смартфон Apple iPhone 13", 799.99, 10),
            ("MacBook Air", "Ноутбук Apple MacBook Air M1", 999.99, 5),
            ("Футболка", "Хлопковая футболка", 19.99, 50)
        ]

        created_products = []
        for name, description, price, stock in products:
            product = marketplace.product_service.create_product(
                seller_id=seller.user_id,
                category_id=1,  # Электроника
                name=name,
                description=description,
                price=price,
                stock_quantity=stock
            )
            created_products.append(product)
            print(f"✅ Товар создан: {product.name} - ${product.price}")

        # Создание заказа
        order_items = [
            {'product_id': created_products[0].product_id, 'quantity': 2},
            {'product_id': created_products[1].product_id, 'quantity': 1}
        ]

        shipping_address = {
            "street": "ул. Примерная, д. 123",
            "city": "Москва",
            "postal_code": "123456",
            "country": "Россия"
        }

        billing_address = {
            "street": "ул. Примерная, д. 123",
            "city": "Москва",
            "postal_code": "123456",
            "country": "Россия"
        }

        order = marketplace.order_service.create_order(
            buyer_id=buyer.user_id,
            items=order_items,
            shipping_address=shipping_address,
            billing_address=billing_address
        )

        if order:
            print(f"✅ Заказ создан: #{order.order_id}")
            print(f"   Сумма: ${order.total_amount}")
            print(f"   Статус: {order.status.value}")
        else:
            print("❌ Не удалось создать заказ")

    except Exception as e:
        print(f"❌ Ошибка в демо-сценарии: {e}")


def show_statistics(marketplace):
    """Показать статистику системы"""
    print("\n📊 Статистика системы:")
    try:
        # Количество пользователей
        users_count = marketplace.db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
        products_count = marketplace.db.execute_query("SELECT COUNT(*) as count FROM products")[0]['count']
        orders_count = marketplace.db.execute_query("SELECT COUNT(*) as count FROM orders")[0]['count']

        print(f"   👥 Пользователей: {users_count}")
        print(f"   📦 Товаров: {products_count}")
        print(f"   🛒 Заказов: {orders_count}")

    except Exception as e:
        print(f"   ❌ Не удалось получить статистику: {e}")


def main():
    """Основная функция запуска"""
    print("🚀 Запуск маркетплейса с SQLite...")

    try:
        # Инициализация SQLite базы данных
        db = SQLiteManager("marketplace.db")

        # Создание сервиса маркетплейса
        marketplace = MarketplaceService(db)
        print("✅ Сервисы инициализированы")

        # Настройка начальных данных
        buyer, seller = setup_initial_data(marketplace)

        if buyer and seller:
            # Запуск демонстрационного сценария
            demo_scenario(marketplace, buyer, seller)

        # Показать статистику
        show_statistics(marketplace)

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if 'db' in locals():
            db.close()
        print("\n👋 Работа маркетплейса завершена")


if __name__ == "__main__":
    main()