from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.userschema import UserSchema


class PantrySchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    dry = fields.String(validate=[validate.Length(max=1000)])
    fridge = fields.String(validate=[validate.Length(max=1000)])
    freezer = fields.String(validate=[validate.Length(max=1000)])

    is_publish = fields.Boolean(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email', ))

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data
