from marshmallow import Schema, fields

__all__ = ("ErrorResponseSchema", "HealthCheckResponseSchema")


class HealthCheckResponseSchema(Schema):
    status = fields.Str(required=True)
    bot_running = fields.Bool(required=True)


class ErrorResponseSchema(Schema):
    error = fields.Str(required=True)
    code = fields.Int(required=False)
