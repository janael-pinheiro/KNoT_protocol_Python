from marshmallow import Schema, ValidationError, fields, post_load
from marshmallow.validate import And, Length, OneOf, Regexp

from knot_protocol.domain.DTO.data_point import DataPointDTO
from knot_protocol.domain.DTO.event import Event
from knot_protocol.domain.DTO.schema import SchemaDTO
from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.infraestructure.utils.knot_amqp_options import KNoTValueType, KNoTPatterns


def is_integer(value):
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise ValidationError("Value must be integer.")
    try:
        int(value, base=10)
    except ValueError as exc:
        raise ValidationError("Value must be integer.") from exc


def is_positive(value):
    if value < 0:
        raise ValidationError("Value must be positive.")


class DataPointSchema(Schema):
    sensorId = fields.Int(
        attribute="sensor_id",
        validate=And(is_integer, is_positive),
        required=True)
    value = fields.Number(required=True)
    timestamp = fields.Str(required=True)

    @post_load
    def make_data_point(self, data, **kwargs):
        return DataPointDTO(**data)


class DataPointsSchema(Schema):
    id = fields.Str(required=True)
    data = fields.List(fields.Nested(DataPointSchema), required=True)


class SensorSchema(Schema):
    typeId = fields.Int(attribute="type_id", required=True)
    unit = fields.Int(attribute="unit", required=True)
    valueType = fields.Int(
        attribute="value_type",
        required=True,
        validate=OneOf(choices=[
            KNoTValueType.INT.value,
            KNoTValueType.FLOAT.value,
            KNoTValueType.BOOL.value,
            KNoTValueType.STRING.value]))
    name = fields.Str(attribute="name", required=True)

    @post_load
    def make_sensor_schema(self, data, **kwargs):
        return SchemaDTO(**data)


class SensorEvent(Schema):
    change = fields.Bool(validate=OneOf(choices=[True, False, 0, 1]), required=True)
    timeSec = fields.Int(attribute="time_seconds", required=True)
    lowerThreshold = fields.Number(attribute="lower_threshold")
    upperThreshold = fields.Number(attribute="upper_threshold")

    @post_load
    def make_event(self, data, **kwargs):
        return Event(**data)


class SensorConfiguration(Schema):
    sensorId = fields.Int(attribute="sensor_id", required=True)
    schema = fields.Nested(SensorSchema, required=True)
    event = fields.Nested(SensorEvent, required=True)


class SchemaConfiguration(Schema):
    config = fields.List(fields.Nested(SensorConfiguration), required=True)

    @post_load
    def make_schame_configuration(self, data, **kwargs):
        return [SchemaDTO(**d) for d in data["config"]]


class DeviceSchema(Schema):
    id = fields.Str(
        attribute="device_id",
        validate=[Length(equal=16), Regexp(regex="[1-9a-f]{16}")],
        required=True)
    config = fields.List(fields.Nested(SensorConfiguration), required=True)
    name = fields.Str(required=True)
    state = fields.Str()
    error = fields.Str()
    token = fields.Str(
        validate=[Length(equal=36), Regexp(regex=KNoTPatterns.TOKEN.value)],
        required=True)

    @post_load
    def make_device(self, data, **kwargs):
        return DeviceEntity(**data)
