import serial
from ts_modbus import connections, modbusRTU_client, const

conn = connections.COMConnection({
    'COM': 'COM1',
    'baudrate': 115200,
    'parity': serial.PARITY_NONE,
    'bytesizes': serial.EIGHTBITS,
    'stopbits': serial.STOPBITS_ONE
})

conn.open_connection()
mb = modbusRTU_client.TSMbRTUClient()

# Read registers
data = mb.execute(conn, function=const.READ_INPUT_REGISTERS, device_address=16, start_address=51, regs_quantity=1)
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

# Write registers
data = mb.execute(conn, function=const.WRITE_SINGLE_REGISTER, device_address=16, start_address=50, values=[1])
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

# Send multiple requests to the device
result = mb.execute_ext(conn, [[1, 1, 0, 10], [2, 1, 0, 10], [3, 1, 0, 10], [4, 1, 0, 10], [6, 1, 12301, 1, [12301]]])
print(result)
print(mb.ts_requests_ext)

conn.close_connection()
