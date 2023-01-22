from marshmallow import Schema, fields


class DeviceAuthRequestDTO(Schema):
    id = fields.Str()
    token = fields.Str()
