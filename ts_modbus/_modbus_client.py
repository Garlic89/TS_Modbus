from struct import pack, unpack
from math import ceil
from datetime import datetime
from . import const
from . import commons as cmn
from .connections import _TSConnection
from .exceptions import (TSModbusInvalidDataSize, TSModbusInvalidResponse, TSModbusInvalidInputParamsType,
                         TSModbusInvalidInputValuesTypes)


class _TSMbClient:
    def __init__(self):
        self.ts_last_request = {
                            'error': 0,
                            'function': 0,
                            'device_address': 0,
                            'start_address': 0,
                            'regs_quantity': 0,
                            'request': b'',
                            'response': b'',
                            'response_time': 0.0,
                            'values': [],
                            'data': []
        }
        self.ts_requests_ext = []

    def execute_ext(self, connection: _TSConnection, requests: []):
        """
        Execute several requests to a device by modbus protocol
        :param connection: Connection control class
        :param requests: Params of the series requests
        :return: []
        """
        data = []
        for i in range(len(requests)):
            result = self.execute(connection, **requests[i])
            data.append(result)
            self.ts_requests_ext.append(self.ts_last_request)
        return data

    def execute(self, connection: _TSConnection, function: int, device_address: int = 0, start_address: int = 0,
                regs_quantity: int = 0, values=[]) -> []:
        """
        Execute single modbus request
        :param connection: Connection control class
        :param function: function number
        :param device_address: address of the slave device
        :param start_address: start register address
        :param regs_quantity: quantity of registers (only for read functions)
        :param values: list of values (only for write functions)
        :return:
        """
        start_time = datetime.now().timestamp()
        try:
            if isinstance(values, int):
                values = [values]
            elif not isinstance(values, list):
                raise TSModbusInvalidInputParamsType({'values': values})
            # Save request params
            self.ts_last_request['function'] = function
            self.ts_last_request['device_address'] = device_address
            self.ts_last_request['start_address'] = start_address
            self.ts_last_request['regs_quantity'] = regs_quantity
            self.ts_last_request['error'] = 0
            self.ts_last_request['request'] = b''
            self.ts_last_request['response'] = b''
            self.ts_last_request['data'] = []
            self.ts_last_request['values'] = values
            self.ts_last_request['response_time'] = 0

            # Get PDU
            bdata = self._get_pdu(function, start_address, regs_quantity, values)
            # Add header
            bdata = self._add_header(bdata)
            # Add CRC
            bdata = self._add_crc(bdata)
            self.ts_last_request['request'] = bdata
            # Send request
            connection.send(bdata)
            # Wait for answer
            response = connection.response()
            self.ts_last_request['response'] = response
            # Check response CRC
            response = self._check_crc(response)
            # Check response header
            response = self._check_response_header(response)
            # Decode PDU data
            self._decode_pdu(function, start_address, regs_quantity, response)
            return self.ts_last_request['data']
        finally:
            self.ts_last_request['response_time'] = (datetime.now().timestamp() - start_time) * 1000

    # noinspection PyMethodMayBeStatic
    def _get_pdu(self, function: int, start_address: int, regs_quantity: int, values: list) -> bytes:
        """
        Generate PDU of modbus request
        """
        # Functions 1, 2, 3, 4
        flist = [const.READ_COILS, const.READ_DISCRETE_INPUTS, const.READ_HOLDING_REGISTER, const.READ_INPUT_REGISTERS]
        if function in flist:
            data = [function, start_address, regs_quantity]
            return pack('>B2H', *data)

        # Function 5, 6
        if function in [const.WRITE_SINGLE_COIL, const.WRITE_SINGLE_REGISTER]:
            if function == const.WRITE_SINGLE_COIL:
                if values[0] > 0:
                    values[0] = 0xFF00
                else:
                    values[0] = 0
            data = [function, start_address, values[0]]
            return pack('>B2H', *data)

        # Function 15
        if function in [const.WRITE_MULTIPLE_COILS]:
            regs_quantity = len(values)
            self.ts_last_request['regs_quantity'] = regs_quantity
            bytes_count = ceil(regs_quantity/8)
            values_str = ''
            for i in reversed(range(regs_quantity)):
                if not isinstance(values[i], int):
                    raise TSModbusInvalidInputValuesTypes(values[i])
                if values[i] > 0:
                    values_str = '1' + values_str
                else:
                    values_str = '0' + values_str

            values_str = '0b' + values_str
            data = [function, start_address, regs_quantity, bytes_count, eval(values_str)]
            return pack('>B2HB' + str(bytes_count) + 'B', *data)

        # Function 16
        if function in [const.WRITE_MULTIPLE_REGISTERS]:
            regs_quantity = len(values)
            self.ts_last_request['regs_quantity'] = regs_quantity
            data = [function, start_address, regs_quantity, regs_quantity * 2] + values
            return pack('>B2HB' + str(regs_quantity) + 'H', *data)

    def _decode_pdu(self, function: int, start_address: int, regs_quantity: int, response: bytes):
        """
        Decode PDU of modbus response
        """
        # Check response for error message
        if self._is_error_response(function, response):
            return
        # Function 1, 2
        if function in [const.READ_COILS, const.READ_DISCRETE_INPUTS]:
            bytes_count = regs_quantity // 8
            if regs_quantity % 8 > 0:
                bytes_count += 1
            if response[1] != bytes_count:
                raise TSModbusInvalidDataSize(response, response[1], bytes_count)
            response = response[2:]
            self.ts_last_request['data'] = cmn.get_bits_status(response)[0:regs_quantity]
            return

        # Function 3, 4
        if function in [const.READ_HOLDING_REGISTER, const.READ_INPUT_REGISTERS]:
            if response[1] != regs_quantity * 2:
                raise TSModbusInvalidDataSize(response, response[1], regs_quantity * 2)
            response = response[2:]
            data = unpack('>' + str(regs_quantity) + 'H', response)
            self.ts_last_request['data'] = data
            return

        # Function 5, 6
        if function in [const.WRITE_SINGLE_COIL, const.WRITE_SINGLE_REGISTER]:
            if self.ts_last_request['response'] != self.ts_last_request['request']:
                raise TSModbusInvalidResponse(self.ts_last_request['request'], response)
            return

        # Function 15, 16
        if function in [const.WRITE_MULTIPLE_COILS, const.WRITE_MULTIPLE_REGISTERS]:
            t_func, t_start_address, t_regs_count = unpack('>B2H', response)
            if t_func != function or t_start_address != start_address or t_regs_count != len(self.ts_last_request['values']):
                raise TSModbusInvalidResponse(self.ts_last_request['request'], response)

    def _is_error_response(self, function: int, pdu: bytes) -> bool:
        """
        Check response for error message
        :param pdu: PDU data block
        :return: True - error exists, False - error is absent
        """
        if pdu[0] == function + 0x80:
            self.ts_last_request['error'] = pdu[1]
            return True
        else:
            self.ts_last_request['error'] = 0
            return False

    # noinspection PyMethodMayBeStatic
    def _check_params_types(self, device_address: int = 0, start_address: int = 0, regs_quantity: int = 0) -> bool:
        """
        Check params types
        """
        if not isinstance(device_address, int) \
                or not isinstance(start_address, int) \
                or not isinstance(regs_quantity, int):
            return False
        else:
            return True

    def _add_header(self, bdata: bytes) -> bytes:
        """Add header to modbus request
        (* This metod must be override in inheritor *)
        """
        return bdata

    def _check_response_header(self, bdata: bytes, remove_after: bool = True) -> bytes:
        """
        Check modbus response header of the slave device
        (* This metod must be override in inheritor *)
        """
        return bdata

    # noinspection PyMethodMayBeStatic
    def _add_crc(self, bdata: bytes) -> bytes:
        """
        Add CRC to modbus request
        (* This metod must be override in inheritor *)
        """
        return bdata

    # noinspection PyMethodMayBeStatic
    def _check_crc(self, bdata: bytes, remove_after: bool = True) -> bytes:
        """
        Check CRC of modbus response
        (* This metod must be override in inheritor *)
        """
        return bdata
