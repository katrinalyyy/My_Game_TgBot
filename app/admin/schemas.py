"""
Схемы для административного API
"""
from marshmallow import Schema, fields, validate


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    is_active = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)


class CreateCategoryRequestSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)


class QuestionSchema(Schema):
    """Схема вопроса"""
    id = fields.Int(dump_only=True)
    category_id = fields.Int(required=True)
    question_text = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    answer_text = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    difficulty = fields.Int(required=True, validate=validate.OneOf([100, 200, 300, 400, 500]))
    is_active = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)


class CreateQuestionRequestSchema(Schema):
    """Схема для создания вопроса"""
    category_id = fields.Int(required=True, validate=validate.Range(min=1))
    question_text = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    answer_text = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    difficulty = fields.Int(required=True, validate=validate.OneOf([100, 200, 300, 400, 500]))


class GameSessionSchema(Schema):
    """Схема игровой сессии для админа"""
    id = fields.Int(dump_only=True)
    chat_id = fields.Int(required=True)
    host_telegram_id = fields.Int(required=True)
    state = fields.Str(dump_only=True)
    started_at = fields.DateTime(dump_only=True)
    finished_at = fields.DateTime(dump_only=True, allow_none=True)
    is_active = fields.Bool(dump_only=True)
    total_participants = fields.Int(dump_only=True)
    total_questions = fields.Int(dump_only=True)


class AdminResponseSchema(Schema):
    """Общая схема ответа админа"""
    success = fields.Bool(required=True)
    message = fields.Str(allow_none=True)
    error = fields.Str(allow_none=True)


class CategoryResponseSchema(Schema):
    """Схема ответа категории"""
    success = fields.Bool(required=True)
    category = fields.Nested(CategorySchema, allow_none=True)
    error = fields.Str(allow_none=True)


class CategoriesListResponseSchema(Schema):
    """Схема ответа списка категорий"""
    success = fields.Bool(required=True)
    categories = fields.List(fields.Nested(CategorySchema))
    total = fields.Int(required=True)
    error = fields.Str(allow_none=True)


class QuestionResponseSchema(Schema):
    """Схема ответа вопроса"""
    success = fields.Bool(required=True)
    question = fields.Nested(QuestionSchema, allow_none=True)
    error = fields.Str(allow_none=True)


class QuestionsListResponseSchema(Schema):
    """Схема ответа списка вопросов"""
    success = fields.Bool(required=True)
    questions = fields.List(fields.Nested(QuestionSchema))
    total = fields.Int(required=True)
    error = fields.Str(allow_none=True)


class GamesListResponseSchema(Schema):
    """Схема ответа списка игр"""
    success = fields.Bool(required=True)
    games = fields.List(fields.Nested(GameSessionSchema))
    total = fields.Int(required=True)
    error = fields.Str(allow_none=True)


class SystemStatsResponseSchema(Schema):
    """Схема ответа системной статистики"""
    success = fields.Bool(required=True)
    stats = fields.Dict(keys=fields.Str(), values=fields.Raw())
    error = fields.Str(allow_none=True)
