from marshmallow import Schema, fields, validate, pre_load, EXCLUDE


class StudentSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    name = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    email = fields.Email(
        required=True,
    )
    phone = fields.String(
        required=True,
        validate=validate.Length(min=8)
    )
    address = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    gender_id = fields.Integer(
        required=True
    )
    status = fields.Boolean(
        required=True
    )

    @pre_load
    def strip_normalize(self, data, **kwargs):
        if 'name' in data and isinstance(data.get('name'), str):
            data['name'] = data['name'].strip()
        if 'email' in data and isinstance(data.get('email'), str):
            data['email'] = data['email'].strip()
            data['email'] = data['email'].lower()
        if 'address' in data and isinstance(data.get('address'), str):
            data['address'] = data['address'].strip()
        return data
