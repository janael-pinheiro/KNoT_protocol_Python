from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import DeviceSchema


def test_given_device_entity_serialize(test_device):
    EXPECT_DEVICE_CONFIGURATION = {
        "id": "1",
        "config": [{
            "event": {
                "lowerThreshold": 4.0,
                "upperThreshold": 10.0,
                "change": True,
                "timeSec": 5},
            "schema": {
                "unit": 0,
                "name": "temperature",
                "valueType": 3,
                "typeId": 65521},
            "sensorId": 1}
            ]}
    device_schema = DeviceSchema()
    serialized_device_configuration = device_schema.dump(test_device)
    assert EXPECT_DEVICE_CONFIGURATION["config"][0]["event"]["upperThreshold"] == serialized_device_configuration["config"][0]["event"]["upperThreshold"]
    assert EXPECT_DEVICE_CONFIGURATION["config"][0]["schema"]["name"] == serialized_device_configuration["config"][0]["schema"]["name"]
    assert EXPECT_DEVICE_CONFIGURATION["config"][0]["sensorId"] == serialized_device_configuration["config"][0]["sensorId"]
