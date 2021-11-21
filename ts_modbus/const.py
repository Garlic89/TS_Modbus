# Modbus Functions Identificators
READ_COILS = 0x01
READ_DISCRETE_INPUTS = 0x02
READ_HOLDING_REGISTER = 0x03
READ_INPUT_REGISTERS = 0x04
WRITE_SINGLE_COIL = 0x05
WRITE_SINGLE_REGISTER = 0x06
WRITE_MULTIPLE_COILS = 0x0F
WRITE_MULTIPLE_REGISTERS = 0x10

# Default Modbus client configuration
MB_DEFAULT_CONFIG = {
    'ip': '127.0.0.1',
    'port': 502,
    'COM': 'COM1',
    'baudrate': 9600,
    'parity': 'none',
    'bytesizes': 8,
    'stopbits': 1
}
