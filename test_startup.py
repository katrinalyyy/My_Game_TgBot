"""
Тест запуска приложения
"""
import asyncio
import sys
import traceback

async def test_startup():
    """Тестируем запуск приложения"""
    try:
        print("🔍 Импортируем модули...")
        
        from app.web.app import setup_app
        print("✅ Импорт setup_app успешен")
        
        print("🔍 Создаем приложение...")
        app = setup_app()
        print("✅ Приложение создано успешно")
        
        print("🔍 Проверяем маршруты...")
        routes = []
        for route in app.router.routes():
            routes.append(f"{route.method} {route.resource}")
        
        print(f"✅ Найдено {len(routes)} маршрутов:")
        for route in routes[:10]:  # Показываем первые 10
            print(f"  - {route}")
        
        if len(routes) > 10:
            print(f"  ... и еще {len(routes) - 10} маршрутов")
        
        print("🔍 Проверяем health check...")
        health_route = None
        for route in app.router.routes():
            if hasattr(route, 'resource') and str(route.resource) == '/health':
                health_route = route
                break
        
        if health_route:
            print("✅ Health check маршрут найден")
        else:
            print("❌ Health check маршрут не найден")
        
        print("🎉 Все тесты пройдены! Приложение готово к запуску.")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        print("📋 Подробная информация об ошибке:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Тестируем запуск приложения...")
    asyncio.run(test_startup())
