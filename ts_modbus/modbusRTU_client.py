import struct
from ._modbus_client import _TSMbClient
from .commons import calculate_crc
from .exceptions import TSModbusInvalidTCPHeader, TSModbusInvalidResponseSize, TSModbusInvalidCRC


class TSMbRTUClient(_TSMbClient):
    """
    Modbus RTU protocol support class
    """
    def __init__(self):
        super().__init__()

    def _add_header(self, bdata: bytes) -> bytes:
        """
        Add Modbus RTU header to request
        """
        header = [self.ts_last_request['device_address']]
        bheader = struct.pack('>B', *header)
        return bheader + bdata

    def _check_response_header(self, bdata: bytes, remove_after: bool = True) -> bytes:
        """
        Check header of modbus RTU response
        """
        if len(bdata) <= 1:
            raise TSModbusInvalidResponseSize
        bheader = bdata[0:1]
        header = struct.unpack('>B', bheader)
        if header[0] != self.ts_last_request['device_address']:
            raise TSModbusInvalidTCPHeader(header)

        # Если проверка прошла успешно - удаляем заголовок
        if remove_after:
            return bdata[1:len(bdata)]
        return bdata

    # noinspection PyMethodMayBeStatic
    def _add_crc(self, bdata: bytes) -> bytes:
        crc = calculate_crc(bdata)
        return bdata + struct.pack('>H', crc)

    # noinspection PyMethodMayBeStatic
    def _check_crc(self, bdata: bytes, remove_after: bool = True) -> bytes:
        calc_crc = calculate_crc(bdata[0:len(bdata)-2])
        calc_crc = struct.pack('>H', calc_crc)
        crc = bdata[len(bdata)-2:len(bdata)]
        if crc != calc_crc:
            raise TSModbusInvalidCRC(crc, calc_crc)
        if remove_after:
            return bdata[0:len(bdata)-2]
        return bdata
