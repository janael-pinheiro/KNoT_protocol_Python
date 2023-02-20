from marshmallow import Schema, fields, post_load

from knot_protocol.domain.boundary.input.DTO.unregistration_response_dto import \
    UnregistrationReponseDTO


class DeviceUnregistrationResponseDTO(Schema):
    id = fields.Str()
    error = fields.Str(allow_none=True)

    @post_load
    def make_unregistration_response(self, data, **kwargs):
        return UnregistrationReponseDTO(**data)
