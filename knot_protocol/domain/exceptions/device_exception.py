class AlreadyRegisteredDeviceException(Exception):
    ...


class AlreadyAuthenticatedException(Exception):
    ...


class AlreadyUpdatedSchema(Exception):
    ...


class AlreadyReady(Exception):
    ...


class NotReadyException(Exception):
    ...


class NotRegistered(Exception):
    ...


class NotUpdatedSchemaException(Exception):
    ...


class NotAuthenticatedException(Exception):
    ...


class AuthenticationErrorException(Exception):
    ...


class UpdateConfigurationException(Exception):
    ...


class DifferentDeviceIdentifierException(Exception):
    ...
