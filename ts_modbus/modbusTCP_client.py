import struct
from ._modbus_client import _TSMbClient
from .exceptions import TSModbusInvalidTCPHeader, TSModbusInvalidResponseSize


class TSMbTCPClient(_TSMbClient):
    """
    Modbus TCP protocol support class
    """

    def __init__(self):
        super().__init__()
        self._transaction_id = 0

    def _add_header(self, bdata: bytes) -> bytes:
        """
        Add header to modbus request (Override method)
        """
        self._inc_transaction_id()
        header = [self._transaction_id, 0, len(bdata) + 1, self.ts_last_request['device_address']]
        bheader = struct.pack('>3HB', *header)
        return bheader + bdata

    def _inc_transaction_id(self) -> int:
        """
        Increment transaction ID of request
        """
        if self._transaction_id >= 65500:
            self._transaction_id = 0
        else:
            self._transaction_id += 1
        return self._transaction_id

    def _check_response_header(self, bdata: bytes, remove_after: bool = True) -> bytes:
        """
        Check modbus response header of the slave device (Override method)
        """
        if len(bdata) <= 7:
            raise TSModbusInvalidResponseSize
        bheader = bdata[0:7]
        header = struct.unpack('>3HB', bheader)
        if (header[0] != self._transaction_id) or (header[1] != 0) or (header[2] != len(bdata) - 6) \
                or (header[3] != self.ts_last_request['device_address']):
            raise TSModbusInvalidTCPHeader(header)

        # remove header
        if remove_after:
            return bdata[7:len(bdata)]
        return bdata
