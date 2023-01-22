from marshmallow import Schema, fields


class DeviceRegistrationRequestDTO(Schema):
    id = fields.Str()
    name = fields.Str()
