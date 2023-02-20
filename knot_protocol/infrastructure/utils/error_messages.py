from enum import Enum


class KNoTErrorMessage(Enum):
    device_exists = "thing is already registered"
    unauthorized_device = "unauthorized to authenticate thing"
    device_not_found = "thing not found on thing's service"
