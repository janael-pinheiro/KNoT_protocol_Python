from marshmallow import Schema, fields, post_load

from knot_protocol.domain.boundary.input.DTO.config_response_dto import ConfigurationUpdateResponseDTO
from knot_protocol.infrastructure.adapter.output.DTO.device_schema import SensorConfiguration


class ConfigUpdateResponseSchema(Schema):
    id = fields.Str()
    config = fields.List(fields.Nested(SensorConfiguration))
    changed = fields.Bool()
    error = fields.Str(allow_none=True)

    @post_load
    def make_config_update_response(self, data, **kwargs):
        return ConfigurationUpdateResponseDTO(**data)
