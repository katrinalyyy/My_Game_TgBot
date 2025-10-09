from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()


class MessageSchema(Schema):
    message_id = fields.Int()
    text = fields.Str()
    from_user = fields.Nested(UserSchema, data_key="from")


class UpdateSchema(Schema):
    update_id = fields.Int(required=True)
    message = fields.Nested(MessageSchema)


class TelegramResponseSchema(Schema):
    ok = fields.Bool(required=True)
    result = fields.List(fields.Nested(UpdateSchema))
