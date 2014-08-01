class OneWireException(Exception):
    pass


class DeviceError(OneWireException):
    pass


class WriteError(OneWireException):
    pass


class CRCError(OneWireException):
    pass
