"""
Схемы для API пользователей
"""
from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    telegram_id = fields.Int(required=True)
    username = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    total_games = fields.Int(dump_only=True)
    total_wins = fields.Int(dump_only=True)
    total_score = fields.Int(dump_only=True)


class CreateUserRequestSchema(Schema):
    telegram_id = fields.Int(required=True, validate=validate.Range(min=1))
    username = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)


class UpdateUserRequestSchema(Schema):
    """Схема для обновления пользователя"""
    username = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)


class UserStatsSchema(Schema):
    """Схема статистики пользователя"""
    telegram_id = fields.Int(required=True)
    username = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    total_games = fields.Int(required=True)
    total_wins = fields.Int(required=True)
    total_score = fields.Int(required=True)
    win_rate = fields.Float(required=True)


class UserResponseSchema(Schema):
    """Схема ответа пользователя"""
    success = fields.Bool(required=True)
    user = fields.Nested(UserSchema, allow_none=True)
    error = fields.Str(allow_none=True)


class UsersListResponseSchema(Schema):
    """Схема ответа списка пользователей"""
    success = fields.Bool(required=True)
    users = fields.List(fields.Nested(UserSchema))
    total = fields.Int(required=True)
    error = fields.Str(allow_none=True)


class UserStatsResponseSchema(Schema):
    """Схема ответа статистики пользователей"""
    success = fields.Bool(required=True)
    stats = fields.List(fields.Nested(UserStatsSchema))
    total = fields.Int(required=True)
    error = fields.Str(allow_none=True)
