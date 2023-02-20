from marshmallow import Schema, fields


class DeviceRegistrationRequestSchema(Schema):
    id = fields.Str()
    name = fields.Str()
