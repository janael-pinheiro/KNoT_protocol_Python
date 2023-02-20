from knot_protocol.infrastructure.adapter.output.repositories.device_file_repository import \
    DeviceFileRepository
from knot_protocol.domain.entities.device_factory import DeviceFactory
from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.domain.boundary.output.DTO.schema import SchemaFactory
from knot_protocol.domain.boundary.output.DTO.event import EventFactory
from knot_protocol.domain.boundary.output.DTO.data_point import DataPointFactory
from knot_protocol.domain.boundary.output.DTO.device_configuration import ConfigurationFactory
from knot_protocol.domain.boundary.output.DTO.knot_amqp_options import KNoTValueType
from knot_protocol.infrastructure.adapter.output.DTO.device_registration_request_DTO import \
    DeviceRegistrationRequestSchema
from knot_protocol.infrastructure.adapter.output.DTO.device_auth_request_DTO import \
    DeviceAuthRequestSchema
from knot_protocol.infrastructure.adapter.output.DTO.device_schema import \
    DataPointsSchema
from knot_protocol.infrastructure.adapter.output.DTO.update_config_schema import \
    UpdateConfigRequestSchema
from knot_protocol.infrastructure.adapter.output.DTO.device_unregistration_request_dto import DeviceUnregistrationRequestDTO
from knot_protocol.infrastructure.adapter.input.amqp_setup import amqp_data_management_setup
from knot_protocol.infrastructure.utils.logger import logger_factory