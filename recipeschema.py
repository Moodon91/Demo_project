from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.userschema import UserSchema


def validate_num_of_servings(n):
    if n < 1:
        raise ValidationError('Number of servings must be greater than 0.')
    if n > 50:
        raise ValidationError('Number of servings cannot exceed 50.')


def validate_duration(n):
    if n < 1:
        raise ValidationError('Duration must be greater than 0.')
    if n > 60000:
        raise ValidationError('Duration must be less than 60000.')


class RecipeSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    duration = fields.Integer(validate=validate_duration)
    num_of_servings = fields.Integer(validate=validate_num_of_servings)
    ingredients = fields.String(validate=[validate.Length(max=1000)])
    directions = fields.String(validate=[validate.Length(max=2000)])
    cost = fields.Integer()

    is_publish = fields.Boolean(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email',))

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data

    @validates('cost')
    def validate_cost(self, value):
        if value < 1:
            raise ValidationError('cost must be greater than 0.')
        if value > 10000:
            raise ValidationError('cost must be less than 10,000. What am I, a millionaire?')
