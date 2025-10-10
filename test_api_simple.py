"""
Простой тест API без Swagger
"""
import asyncio
import aiohttp
import json

async def test_api():
    """Тестируем основные эндпоинты API"""
    base_url = "http://localhost:8085"
    
    async with aiohttp.ClientSession() as session:
        # Тест health check
        print("🔍 Тестируем health check...")
        try:
            async with session.get(f"{base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check: {data}")
                else:
                    print(f"❌ Health check failed: {resp.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Тест создания пользователя
        print("\n👤 Тестируем создание пользователя...")
        try:
            user_data = {
                "telegram_id": 123456789,
                "username": "test_user",
                "first_name": "Тестовый",
                "last_name": "Пользователь"
            }
            async with session.post(
                f"{base_url}/api/v1/users", 
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Пользователь создан: {data}")
                else:
                    text = await resp.text()
                    print(f"❌ Создание пользователя failed: {resp.status} - {text}")
        except Exception as e:
            print(f"❌ Ошибка создания пользователя: {e}")
        
        # Тест получения категорий
        print("\n📚 Тестируем получение категорий...")
        try:
            async with session.get(f"{base_url}/api/v1/admin/categories") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Категории получены: {data}")
                else:
                    text = await resp.text()
                    print(f"❌ Получение категорий failed: {resp.status} - {text}")
        except Exception as e:
            print(f"❌ Ошибка получения категорий: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования API...")
    asyncio.run(test_api())
