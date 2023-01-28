from marshmallow import Schema, fields, post_load
from knot_protocol_python.domain.DTO.device_configuration import SchemaDTO
from knot_protocol_python.domain.entities.device_entity import DeviceEntity


class DataPointSchema(Schema):
    sensorId = fields.Int(attribute="sensor_id")
    value = fields.Number()
    timestamp = fields.Str()


class DataPointsSchema(Schema):
    id = fields.Str()
    data = fields.List(fields.Nested(DataPointSchema))


class SensorSchema(Schema):
    typeId = fields.Int(attribute="type_id")
    unit = fields.Int(attribute="unit")
    valueType = fields.Int(attribute="value_type")
    name = fields.Str(attribute="name")


class SensorEvent(Schema):
    change = fields.Bool()
    timeSec = fields.Int(attribute="time_seconds")
    lowerThreshold = fields.Number(attribute="lower_threshold")
    upperThreshold = fields.Number(attribute="upper_threshold")


class SensorConfiguration(Schema):
    sensorId = fields.Int(attribute="sensor_id")
    schema = fields.Nested(SensorSchema)
    event = fields.Nested(SensorEvent)


class SchemaConfiguration(Schema):
    config = fields.List(fields.Nested(SensorConfiguration))

    @post_load
    def make_schame_configuration(self, data, **kwargs):
        return [SchemaDTO(**d) for d in data["config"]]


class DeviceSchema(Schema):
    id = fields.Str(attribute="device_id")
    config = fields.List(fields.Nested(SensorConfiguration))
    name = fields.Str()
    state = fields.Str()
    error = fields.Str()
    token = fields.Str()

    @post_load
    def make_device(self, data, **kwargs):
        return DeviceEntity(**data)
