
class TSModbusInvalidCRC(Exception):
    """Exception raised when crc of response is invalid"""
    def __init__(self, crc, calc_crc: bytes):
        msg = "CRC of modbus response is invalid!"
        msg = msg + f'\ncrc: {crc}' + f'\ncalculated crc: {calc_crc}'
        super().__init__(msg)


class TSModbusInvalidInputParamsType(Exception):
    """Exception raised when types of input params is not valid"""
    def __init__(self, params: dict):
        msg = "Types of input params for generate modbus request is incorrect"
        for key in params:
            msg = msg + f'\n{key}: {type(params[key])}'
        super().__init__(msg)


class TSModbusInvalidInputValuesTypes(Exception):
    """Exception raised when types of input values is not valid"""
    def __init__(self, value):
        msg = "Types of input values for generate modbus write request is incorrect"
        msg = msg + f'\n{value}: {type(value)}'
        super().__init__(msg)


class TSModbusInvalidResponseSize(Exception):
    """Exception raised when response size is less then it's need"""
    def __init__(self):
        super().__init__(
            "Size of response is very small"
        )


class TSModbusDeviceNoResponse(Exception):
    """Exception raised when the device not response"""
    def __init__(self):
        super().__init__(
            "Device no response"
        )


class TSModbusInvalidResponse(Exception):
    """Exception raised when response is not equal request"""
    def __init__(self, request, response: bytes):
        super().__init__(
            "Modbus response have to be equal for response for this request function"
            f"\nrequest: {request} "
            f"\nresponse: {response} "
        )


class TSModbusInvalidTCPHeader(Exception):
    """Exception raised when params in ts_modbus header is not valid"""
    def __init__(self, header: bytes):
        super().__init__(
            "Modbus header of response is not valid"
            f"\nheader: {header} "
        )


class TSModbusInvalidDataSize(Exception):
    """Exception raised when response data size is not valid"""
    def __init__(self, pdu: bytes, r_value, n_value: int):
        super().__init__(
            "Response data size is not valid"
            f"\npdu: {pdu} "
            f"\nCurrent Value: {r_value} "
            f"\nNeed Value: {n_value} "
        )


