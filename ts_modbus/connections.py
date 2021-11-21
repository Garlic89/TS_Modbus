import socket
import serial
import ipaddress
import ts_modbus.const as const


class _TSConnection:

    def __init__(self, config: dict):
        self.config = const.MB_DEFAULT_CONFIG
        if not self._check_config(config):
            config = const.MB_DEFAULT_CONFIG
        self.config = config

    # noinspection PyMethodMayBeStatic
    def _check_config(self, config: dict) -> bool:
        return False

    def send(self, data: bytes) -> bool:
        pass

    def response(self) -> bytes:
        pass

    def open_connection(self, timeout: int = 10) -> bool:
        pass

    def close_connection(self) -> bool:
        pass


class COMConnection(_TSConnection):
    def __init__(self, config: dict):
        super().__init__(config)
        self.serialPort = None
        self.COMPort = str(self.config.get('COM', ''))
        self.baudrate = int(self.config.get('baudrate', -1))
        self.parity = str(self.config.get('parity', serial.serialutil.PARITY_NONE))
        self.stopbits = int(self.config.get('stopbits', serial.serialutil.STOPBITS_ONE))
        self.bytesizes = int(self.config.get('bytesizes', serial.serialutil.EIGHTBITS))

    def open_connection(self, timeout: int = 10) -> bool:
        self.serialPort = serial.Serial(port=self.COMPort,
                                        baudrate=self.baudrate,
                                        parity=self.parity,
                                        stopbits=self.stopbits,
                                        bytesize=self.bytesizes,
                                        timeout=timeout)
        return False

    def close_connection(self) -> bool:
        if self.serialPort is not None:
            self.serialPort.close()
        del self.serialPort
        return True

    def send(self, data: bytes) -> bool:
        if self.serialPort is None:
            return False
        if len(data) <= 0:
            return False
        self.serialPort.write(data)
        return True

    def response(self) -> bytes:
        if self.serialPort is None:
            return b''
        try:
            recv = self.serialPort.read(254)
            return recv
        except Exception:
            return b''

    def _check_config(self, config: dict) -> bool:
        if not isinstance(config, dict):
            return False
        COMPort = str(config.get('COM', ''))
        if len(COMPort) <= 0:
            return False
        baudrate = int(config.get('baudrate', -1))
        if baudrate not in serial.SerialBase.BAUDRATES:
            return False
        parity = str(config.get('parity', serial.PARITY_NONE))
        if parity not in serial.SerialBase.PARITIES:
            return False
        stopbits = int(config.get('stopbits', serial.STOPBITS_ONE))
        if stopbits not in serial.SerialBase.STOPBITS:
            return False
        bytesizes = int(config.get('bytesizes', serial.EIGHTBITS))
        if bytesizes not in serial.SerialBase.BYTESIZES:
            return False

        return True


class TCPConnection(_TSConnection):
    def __init__(self, config: dict):
        super().__init__(config)
        self.sock: socket.socket = None

    def open_connection(self, timeout: int = 10) -> bool:
        ip = self.config.get('ip')
        port = self.config.get('port')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(timeout > 0)
            self.sock.settimeout(timeout)
            self.sock.connect((ip, port))
            return True
        except ConnectionRefusedError:
            return False
        except Exception:
            return False

    def close_connection(self) -> bool:
        self.sock.close()
        del self.sock
        return True

    def send(self, data: bytes) -> bool:
        if self.sock is None:
            return False
        if len(data) <= 0:
            return False
        try:
            self.sock.send(data)
            return True
        except Exception:
            return False

    def response(self) -> bytes:
        if self.sock is None:
            return b''
        try:
            recv = self.sock.recv(2048)
            return recv
        except Exception:
            return b''

    def _check_config(self, config: dict) -> bool:
        if not isinstance(config, dict):
            return False
        ipaddress.ip_address(config.get('ip', ''))
        port = int(config.get('port', -1))
        if port > 65535 or port <= 0:
            return False
        return True
