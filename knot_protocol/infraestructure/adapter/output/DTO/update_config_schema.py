from marshmallow import Schema, fields

from knot_protocol.infraestructure.adapter.output.DTO.device_schema import SensorConfiguration


class UpdateConfigRequestSchema(Schema):
    id = fields.Str()
    config = fields.List(fields.Nested(SensorConfiguration))
