from marshmallow import Schema, fields, post_load
from knot_protocol_python.domain.boundary.input.DTO.registration_response_dto import RegistrationResponseDTO

class DeviceRegistrationResponseDTO(Schema):
    id = fields.Str()
    name = fields.Str()
    token = fields.Str()
    error = fields.Str(allow_none=True)

    @post_load
    def make_registration_response(self, data, **kwargs):
        return RegistrationResponseDTO(**data)
