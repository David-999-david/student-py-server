from marshmallow import fields, validate, pre_load, EXCLUDE, Schema


class CourseSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    name = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    student_limit = fields.Integer(
        required=True,
        validate=validate.Range(min=5)
    )
    start_date = fields.DateTime(
    )
    end_date = fields.DateTime()
    status = fields.Boolean(
        required=True
    )

    @pre_load
    def strip_normalize(self, data, **kwargs):
        for k in ("name", "description"):
            if k in data and isinstance(data.get(k), str):
                data[k] = data[k].strip()
        return data
