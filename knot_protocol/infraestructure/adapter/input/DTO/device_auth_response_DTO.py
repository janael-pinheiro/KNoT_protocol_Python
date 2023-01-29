from marshmallow import Schema, fields, post_load
from knot_protocol.domain.boundary.input.DTO.auth_response_dto import AuthResponseDTO


class AuthDeviceResponseDTO(Schema):
    id = fields.Str()
    error = fields.Str(allow_none=True)

    @post_load
    def make_auth_response(self, data, **kwargs):
        return AuthResponseDTO(**data)
