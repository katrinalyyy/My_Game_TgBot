# 🚀 API для Telegram бота "Своя игра"

## ✅ Что реализовано

Полноценное REST API для управления игрой "Своя игра" в Telegram боте.

### 🎮 Игровое API
- **POST** `/api/v1/games` - Создать новую игру
- **POST** `/api/v1/games/join` - Присоединиться к игре
- **POST** `/api/v1/games/begin` - Начать игру
- **POST** `/api/v1/games/board` - Получить игровую доску
- **POST** `/api/v1/games/select-question` - Выбрать вопрос
- **POST** `/api/v1/games/answer` - Ответить на вопрос
- **POST** `/api/v1/games/leaderboard` - Получить таблицу лидеров
- **POST** `/api/v1/games/finish` - Завершить игру

### 👥 Пользовательское API
- **POST** `/api/v1/users` - Создать пользователя
- **GET** `/api/v1/users` - Получить список пользователей
- **GET** `/api/v1/users/{telegram_id}` - Получить пользователя
- **GET** `/api/v1/users/stats` - Получить статистику пользователей

### 🔧 Административное API
- **POST** `/api/v1/admin/categories` - Создать категорию
- **GET** `/api/v1/admin/categories` - Получить категории
- **POST** `/api/v1/admin/questions` - Создать вопрос
- **GET** `/api/v1/admin/questions` - Получить вопросы
- **GET** `/api/v1/admin/games` - Получить игры
- **GET** `/api/v1/admin/stats` - Системная статистика

### 🔍 Мониторинг
- **GET** `/health` - Проверка состояния системы

## 🚀 Запуск

1. **Убедитесь, что PostgreSQL запущен** на порту 5433
2. **Запустите приложение:**
   ```bash
   python main.py
   ```
3. **API будет доступно по адресу:** `http://localhost:8085`
4. **Swagger документация:** `http://localhost:8085/api/docs`

## 📖 Примеры использования

### Создать пользователя
```bash
curl -X POST http://localhost:8085/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "username": "test_user",
    "first_name": "Тестовый"
  }'
```

### Создать игру
```bash
curl -X POST http://localhost:8085/api/v1/games \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890,
    "host_telegram_id": 123456789
  }'
```

### Получить системную статистику
```bash
curl -X GET http://localhost:8085/api/v1/admin/stats
```

## 🧪 Тестирование

Запустите простой тест API:
```bash
python test_api_simple.py
```

## 📊 Структура ответов

### Успешный ответ
```json
{
  "success": true,
  "data": { ... }
}
```

### Ошибка
```json
{
  "success": false,
  "error": "Описание ошибки"
}
```

## 🔧 Технические детали

- **Фреймворк:** aiohttp
- **База данных:** PostgreSQL с SQLAlchemy ORM
- **Валидация:** Marshmallow схемы (готовы для Swagger)
- **Архитектура:** Модульная с разделением на слои

## 📝 Примечания

- Swagger документация временно отключена для стабильности
- API полностью интегрировано с логикой Telegram бота
- Все эндпоинты возвращают JSON с полной обработкой ошибок
- Поддерживается пагинация для списков

## 🎯 Готово для продакшена

API готово для использования в продакшене с добавлением:
- Аутентификации (API ключи, JWT)
- Rate limiting
- Логирования
- Мониторинга
