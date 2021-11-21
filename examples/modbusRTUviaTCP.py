from ts_modbus import connections, modbusRTU_client, const

conn = connections.TCPConnection({
    'ip': '10.100.3.232',
    'port': 4001
})

conn.open_connection(timeout=1)
mb = modbusRTU_client.TSMbRTUClient()

# Read registers
data = mb.execute(conn, function=const.READ_INPUT_REGISTERS, device_address=16, start_address=51, regs_quantity=1)
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

# Write registers
data = mb.execute(conn, function=const.WRITE_MULTIPLE_REGISTERS, device_address=16, start_address=50, values=[1])
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')

# Send multiple requests to the device
result = mb.execute_ext(conn, [{'function': const.READ_INPUT_REGISTERS,
                                'device_address': 16,
                                'start_address': 51,
                                'regs_quantity': 1},
                               {'function': const.READ_INPUT_REGISTERS,
                                'device_address': 16,
                                'start_address': 52,
                                'regs_quantity': 1},
                               {'function': const.WRITE_MULTIPLE_REGISTERS,
                                'device_address': 16,
                                'start_address': 50,
                                'values': [1]},
                               {'function': const.WRITE_MULTIPLE_REGISTERS,
                                'device_address': 16,
                                'start_address': 50,
                                'values': [0]},
                               ])
print(result)
print(mb.ts_requests_ext)

conn.close_connection()
