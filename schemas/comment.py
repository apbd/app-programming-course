from marshmallow import Schema, fields, post_dump, validate


class CommentSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    content = fields.String(required=True, validate=[validate.Length(max=1000)])
    author = fields.String(validate=[validate.Length(max=100)])
    is_publish = fields.Boolean(dump_only=True)
    cover_url = fields.Method(serialize='dump_cover_url')

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data
