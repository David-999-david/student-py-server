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
    current_students = fields.Integer(
        required=True,
        validate=validate.Range(min=0)
    )
    start_date = fields.DateTime(
    )
    end_date = fields.DateTime()

    @pre_load
    def strip_normalize(self, data, **kwargs):
        for k in ("name", "description"):
            if k in data and isinstance(data.get(k), str):
                data[k] = data[k].strip()
        return data
