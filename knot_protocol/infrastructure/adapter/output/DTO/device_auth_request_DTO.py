from marshmallow import Schema, fields


class DeviceAuthRequestSchema(Schema):
    id = fields.Str()
    token = fields.Str()
