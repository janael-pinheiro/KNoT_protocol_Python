from typing import List

from marshmallow import Schema

from knot_protocol.domain.boundary.input.subscriber import Subscriber
from knot_protocol.domain.boundary.output.publisher import Publisher
from knot_protocol.domain.boundary.output.device_persistence_gateway import DevicePersistenceGateway
from knot_protocol.domain.boundary.output.DTO.device_configuration import ConfigurationDTO
from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.domain.usecase.states import (AuthenticatedState,
                                                 CommonStateOperation,
                                                 DisconnectedState, ReadyState,
                                                 RegisteredState,
                                                 UnregisteredState,
                                                 UpdatedSchemaState)


def state_machine_assembler(
    register_subscriber: Subscriber,
    auth_subscriber: Subscriber,
    update_config_subscriber: Subscriber,
    register_publisher: Publisher,
    auth_publisher: Publisher,
    update_config_publisher: Publisher,
    data_publisher: Publisher,
    unregister_subscriber: Publisher,
    unregister_publisher: Publisher,
    unregister_serializer: Schema,
    register_serializer: Schema,
    update_config_serializer: Schema,
    device_auth_serializer: Schema,
    publisher_serializer: Schema
    ):

    common_operation = CommonStateOperation(
        unregister_subscriber=unregister_subscriber,
        unregister_publisher=unregister_publisher,
        device=None,
        unregister_serializer=unregister_serializer,
        unregister_state=None,
        register_publisher=register_publisher,
        register_subscriber=register_subscriber,
        register_serializer=register_serializer,
        register_state=None)
    
    ready_state = ReadyState(
        publisher=data_publisher,
        publisher_serializer=publisher_serializer,
        common_operation=common_operation)

    updated_schema_state = UpdatedSchemaState(ready_state=ready_state, common_operation=common_operation)
    authenticated_state = AuthenticatedState(
        publisher=update_config_publisher,
        subscriber=update_config_subscriber,
        request_serializer=update_config_serializer,
        updated_schema_state=updated_schema_state,
        common_operation=common_operation)

    registered_state = RegisteredState(
        publisher=auth_publisher,
        subscriber=auth_subscriber,
        request_serializer=device_auth_serializer,
        authenticated=authenticated_state,
        common_operation=common_operation)

    unregistered_state = UnregisteredState(common_operation=common_operation)

    common_operation.unregister_state = unregistered_state

    disconnected_state = DisconnectedState(
        authenticate_publisher=auth_publisher,
        authenticate_subscriber=auth_subscriber,
        registered_state=registered_state,
        authenticated=authenticated_state,
        authenticate_serializer=device_auth_serializer,
        common_operation=common_operation)

    return disconnected_state


class DeviceFactory():

    @classmethod
    def __validate_sensor_uniqueness(cls, schema: List[ConfigurationDTO]):
        number_sensors: int = len(schema)
        unique_sensors = set(schema)
        number_unique_sensores = len(unique_sensors)
        if number_sensors != number_unique_sensores:
            raise Exception("Sensors with duplicate identifiers.")

    @classmethod
    def create(
        cls,
        device_id: str,
        name: str,
        schema: List[ConfigurationDTO],
        amqp_generator,
        register_subscriber: Subscriber,
        auth_subscriber: Subscriber,
        update_config_subscriber: Subscriber,
        register_publisher: Publisher,
        auth_publisher: Publisher,
        update_config_publisher: Publisher,
        data_publisher: Publisher,
        unregister_subscriber: Publisher,
        unregister_publisher: Publisher,
        unregister_serializer: Schema,
        register_serializer: Schema,
        update_config_serializer: Schema,
        device_auth_serializer: Schema,
        publisher_serializer: Schema) -> DeviceEntity:
        cls.__validate_sensor_uniqueness(schema=schema)
        disconnected_state = state_machine_assembler(
            auth_publisher=auth_publisher,
            auth_subscriber=auth_subscriber,
            data_publisher=data_publisher,
            device_auth_serializer=device_auth_serializer,
            publisher_serializer=publisher_serializer,
            register_publisher=register_publisher,
            register_subscriber=register_subscriber,
            register_serializer=register_serializer,
            unregister_publisher=unregister_publisher,
            unregister_serializer=unregister_serializer,
            unregister_subscriber=unregister_subscriber,
            update_config_publisher=update_config_publisher,
            update_config_serializer=update_config_serializer,
            update_config_subscriber=update_config_subscriber)

        device = DeviceEntity(
            device_id=device_id,
            name=name,
            config=schema,
            state=disconnected_state,
            data=[None],
            error="",
            token="",
            amqp_generator=amqp_generator)
        device.transition_to_state(disconnected_state)
        return device

    @classmethod
    def configure_existing_device(
        cls,
        device: DeviceEntity,
        amqp_generator,
        register_subscriber: Subscriber,
        auth_subscriber: Subscriber,
        update_config_subscriber: Subscriber,
        register_publisher: Publisher,
        auth_publisher: Publisher,
        update_config_publisher: Publisher,
        data_publisher: Publisher,
        unregister_subscriber: Publisher,
        unregister_publisher: Publisher,
        unregister_serializer: Schema,
        register_serializer: Schema,
        update_config_serializer: Schema,
        device_auth_serializer: Schema,
        publisher_serializer: Schema) -> DeviceEntity:
        disconnected_state = state_machine_assembler(
            auth_publisher=auth_publisher,
            auth_subscriber=auth_subscriber,
            data_publisher=data_publisher,
            device_auth_serializer=device_auth_serializer,
            publisher_serializer=publisher_serializer,
            register_publisher=register_publisher,
            register_subscriber=register_subscriber,
            register_serializer=register_serializer,
            unregister_publisher=unregister_publisher,
            unregister_serializer=unregister_serializer,
            unregister_subscriber=unregister_subscriber,
            update_config_publisher=update_config_publisher,
            update_config_serializer=update_config_serializer,
            update_config_subscriber=update_config_subscriber)
        device.amqp_generator = amqp_generator
        device.transition_to_state(disconnected_state)
        return device
