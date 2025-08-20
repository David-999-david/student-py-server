from marshmallow import Schema, fields, validate, pre_load, EXCLUDE


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=6)
    )

    @pre_load
    def strip_normalize(self, data, **kwargs):
        for k in ("email", "password"):
            if k in data and isinstance(data.get(k), str):
                data[k] = data[k].strip()
        if "email" in data and isinstance(data.get('email'), str):
            data['email'] = data['email'].lower()
        return data
