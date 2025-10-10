# API Примеры использования

## Обзор

Этот проект содержит полноценное REST API для управления игрой "Своя игра" в Telegram боте.

### Основные возможности API:
- 🎮 Управление играми (создание, присоединение, начало, завершение)
- 👥 Управление пользователями
- 📊 Административные функции
- 📚 Swagger документация

## Документация API

После запуска приложения API доступно по адресу:
- **http://localhost:8085** - основной адрес API

## Примеры использования

### 1. Игровое API

#### Создать новую игру
```bash
curl -X POST http://localhost:8085/api/v1/games \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890,
    "host_telegram_id": 123456789
  }'
```

#### Присоединиться к игре
```bash
curl -X POST http://localhost:8080/api/v1/games/join \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890,
    "player_telegram_id": 987654321,
    "username": "player1",
    "first_name": "Игрок"
  }'
```

#### Начать игру
```bash
curl -X POST http://localhost:8080/api/v1/games/begin \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890
  }'
```

#### Получить игровую доску
```bash
curl -X POST http://localhost:8080/api/v1/games/board \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890
  }'
```

#### Выбрать вопрос
```bash
curl -X POST http://localhost:8080/api/v1/games/select-question \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890,
    "category": "Культура",
    "difficulty": 300
  }'
```

#### Ответить на вопрос
```bash
curl -X POST http://localhost:8080/api/v1/games/answer \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890,
    "player_telegram_id": 987654321,
    "answer_text": "Москва"
  }'
```

#### Получить таблицу лидеров
```bash
curl -X POST http://localhost:8080/api/v1/games/leaderboard \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890
  }'
```

### 2. Пользовательское API

#### Создать пользователя
```bash
curl -X POST http://localhost:8085/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "username": "user1",
    "first_name": "Пользователь",
    "last_name": "Тестовый"
  }'
```

#### Получить пользователя
```bash
curl -X GET http://localhost:8085/api/v1/users/123456789
```

#### Получить список пользователей
```bash
curl -X GET "http://localhost:8085/api/v1/users?page=1&limit=10"
```

#### Получить статистику пользователей
```bash
curl -X GET "http://localhost:8085/api/v1/users/stats?sort_by=total_score&page=1&limit=10"
```

### 3. Административное API

#### Создать категорию
```bash
curl -X POST http://localhost:8085/api/v1/admin/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Наука",
    "description": "Вопросы о науке и технологиях"
  }'
```

#### Создать вопрос
```bash
curl -X POST http://localhost:8080/api/v1/admin/questions \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "question_text": "Какой химический элемент имеет символ H?",
    "answer_text": "Водород",
    "difficulty": 100
  }'
```

#### Получить системную статистику
```bash
curl -X GET http://localhost:8085/api/v1/admin/stats
```

#### Получить список игр
```bash
curl -X GET "http://localhost:8085/api/v1/admin/games?page=1&limit=10&active_only=true"
```

## Структура ответов

### Успешный ответ
```json
{
  "success": true,
  "message": "Операция выполнена успешно",
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

## Коды ответов

- **200** - Успешно
- **400** - Ошибка валидации данных
- **404** - Ресурс не найден
- **500** - Внутренняя ошибка сервера

## Аутентификация

В текущей версии API не требует аутентификации. В продакшене рекомендуется добавить:
- API ключи
- JWT токены
- Rate limiting

## Мониторинг

API предоставляет эндпоинт для проверки состояния:
```bash
curl -X GET http://localhost:8085/health
```

Ответ:
```json
{
  "status": "ok",
  "timestamp": "2025-01-09T10:30:00Z"
}
```

## Интеграция с Telegram ботом

API полностью интегрирован с Telegram ботом. Все команды бота используют те же методы, что доступны через API, обеспечивая консистентность данных и логики.
