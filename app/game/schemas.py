"""
Схемы для API игр
"""
from marshmallow import Schema, fields, validate


class GameSessionSchema(Schema):
    id = fields.Int(dump_only=True)
    chat_id = fields.Int(required=True)
    host_telegram_id = fields.Int(required=True)
    state = fields.Str(dump_only=True)
    started_at = fields.DateTime(dump_only=True)
    finished_at = fields.DateTime(dump_only=True, allow_none=True)
    is_active = fields.Bool(dump_only=True)


class CreateGameRequestSchema(Schema):
    chat_id = fields.Int(required=True, validate=validate.Range(min=1))
    host_telegram_id = fields.Int(required=True, validate=validate.Range(min=1))


class JoinGameRequestSchema(Schema):
    chat_id = fields.Int(required=True, validate=validate.Range(min=1))
    player_telegram_id = fields.Int(required=True, validate=validate.Range(min=1))
    username = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)


class GameBoardSchema(Schema):
    category_name = fields.Str(required=True)
    difficulty = fields.Int(required=True)
    is_answered = fields.Bool(required=True)
    answered_by_telegram_id = fields.Int(allow_none=True)
    answered_at = fields.DateTime(allow_none=True)


class GameBoardResponseSchema(Schema):
    success = fields.Bool(required=True)
    board = fields.Dict(keys=fields.Str(), values=fields.List(fields.Nested(GameBoardSchema)))
    game_state = fields.Str()
    error = fields.Str(allow_none=True)


class SelectQuestionRequestSchema(Schema):
    chat_id = fields.Int(required=True, validate=validate.Range(min=1))
    category = fields.Str(required=True)
    difficulty = fields.Int(required=True, validate=validate.OneOf([100, 200, 300, 400, 500]))


class AnswerRequestSchema(Schema):
    chat_id = fields.Int(required=True, validate=validate.Range(min=1))
    player_telegram_id = fields.Int(required=True, validate=validate.Range(min=1))
    answer_text = fields.Str(required=True, validate=validate.Length(min=1, max=500))


class GameResponseSchema(Schema):
    success = fields.Bool(required=True)
    message = fields.Str(allow_none=True)
    error = fields.Str(allow_none=True)
    game_id = fields.Int(allow_none=True)
    total_players = fields.Int(allow_none=True)
    total_questions = fields.Int(allow_none=True)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True)
    category = fields.Str(required=True)
    difficulty = fields.Int(required=True)


class QuestionResponseSchema(Schema):
    success = fields.Bool(required=True)
    question = fields.Nested(QuestionSchema, allow_none=True)
    error = fields.Str(allow_none=True)


class AnswerResponseSchema(Schema):
    success = fields.Bool(required=True)
    is_correct = fields.Bool(allow_none=True)
    correct_answer = fields.Str(allow_none=True)
    score_change = fields.Int(allow_none=True)
    error = fields.Str(allow_none=True)


class ChatIdRequestSchema(Schema):
    chat_id = fields.Int(required=True, validate=validate.Range(min=1))


class LeaderboardResponseSchema(Schema):
    success = fields.Bool(required=True)
    leaderboard = fields.List(fields.Dict())
    error = fields.Str(allow_none=True)
