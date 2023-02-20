from marshmallow import Schema, fields


class DeviceUnregistrationRequestDTO(Schema):
    id = fields.Str()
    name = fields.Str()