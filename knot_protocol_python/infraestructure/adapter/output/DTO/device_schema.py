from marshmallow import Schema, fields


class DataPointSchema(Schema):
    sensorId = fields.Int(attribute="sensorID")
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


class DeviceSchema(Schema):
    id = fields.Str(attribute="device_id")
    config = fields.List(fields.Nested(SensorConfiguration))
    name = fields.Str()
    state = fields.Str()
    error = fields.Str()
    token = fields.Str()
