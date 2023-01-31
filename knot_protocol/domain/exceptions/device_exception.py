class AlreadyRegisteredDeviceException(Exception):
    ...


class AlreadyUnregisteredDeviceException(Exception):
    ...


class AlreadyAuthenticatedException(Exception):
    ...


class AlreadyUpdatedSchema(Exception):
    ...


class AlreadyReady(Exception):
    ...


class NotReadyException(Exception):
    ...


class NotRegisteredException(Exception):
    ...


class NotUpdatedSchemaException(Exception):
    ...


class NotAuthenticatedException(Exception):
    ...


class AuthenticationErrorException(Exception):
    ...


class UpdateConfigurationException(Exception):
    ...


class UnregisteredException(Exception):
    ...


class DifferentDeviceIdentifierException(Exception):
    ...
