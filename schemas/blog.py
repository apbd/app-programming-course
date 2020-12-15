from flask import url_for
from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError

from schemas.user import UserSchema





class BlogSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    blog_title = fields.String(required=True, validate=[validate.Length(max=100)])
    blog_status = fields.String(validate=[validate.Length(max=700)])
    rating = fields.Integer(validate=validate_rating)
    author = fields.String(validate=[validate.Length(max=100)])
    is_publish = fields.Boolean(dump_only=True)
    cover_url = fields.Method(serialize='dump_cover_url')

    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email', ))

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data

    @validates('rating')
    def validate_rating(self, n):
        if n < 1:
            raise ValidationError('Rating must be greater than 0.')
        if n > 10:
            raise ValidationError('Rating must not be greater than 10.')

    def dump_cover_url(self, blog):
        if blog.cover_image:
            return url_for('static', filename='images/blogs/{}'.format(blog.cover_image), _external=True)
        else:
            return url_for('static', filename='images/assets/default-blog-cover.jpg', _external=True)