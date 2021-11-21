from ts_modbus import connections, modbusTCP_client, const

conn = connections.TCPConnection({
    'ip': '10.100.3.231',
    'port': 502
})

conn.open_connection()
mb = modbusTCP_client.TSMbTCPClient()

# Read registers
data = mb.execute(conn, function=const.READ_INPUT_REGISTERS, device_address=1, start_address=0, regs_quantity=10)
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

data = mb.execute(conn, function=const.READ_INPUT_REGISTERS, device_address=1, start_address=20, regs_quantity=5)
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

# Write registers
data = mb.execute(conn, function=const.WRITE_MULTIPLE_REGISTERS, device_address=1, start_address=500, values=[1, 2, 3])
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

# Send multiple requests to the device
result = mb.execute_ext(conn, [{'function': const.READ_INPUT_REGISTERS,
                                'device_address': 1,
                                'start_address': 12300,
                                'regs_quantity': 3},
                               {'function': const.WRITE_MULTIPLE_REGISTERS,
                                'device_address': 1,
                                'start_address': 12300,
                                'values': [1, 2, 3]},
                               {'function': const.READ_INPUT_REGISTERS,
                                'device_address': 1,
                                'start_address': 12300,
                                'regs_quantity': 3},
                               {'function': const.WRITE_MULTIPLE_REGISTERS,
                                'device_address': 1,
                                'start_address': 12300,
                                'values': [0, 0, 0]}
                               ])
print(result)
print(mb.ts_requests_ext)

conn.close_connection()
