from marshmallow import Schema, fields, validate


class PaginationQuerySchema(Schema):
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    limit = fields.Int(missing=20, validate=validate.Range(min=1, max=100))


class UserStatsQuerySchema(Schema):
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    limit = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(missing="total_score", validate=validate.OneOf(["total_score", "total_wins", "win_rate"]))


class QuestionsQuerySchema(Schema):
    category_id = fields.Int(allow_none=True)
    difficulty = fields.Int(allow_none=True, validate=validate.OneOf([100, 200, 300, 400, 500]))
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    limit = fields.Int(missing=20, validate=validate.Range(min=1, max=100))


class GamesQuerySchema(Schema):
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    limit = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    active_only = fields.Bool(missing=False)
