# TS_Modbus: Connect to devices by protocol modbus TCP/RTU

TSModbus allows you to communicate with slave devices by Modbus TCP, RTU and RTU via TCP protocols. Now TSModbus supports the mode of Master.

This module requires only one dependency. It is `serial` to work through a com port.

This module was written for the reason that I needed to know a little more about the request in my projects than the existing packages could provide. I hope that TS_Modbus will also be useful to someone.

# How it works
Create connection class for your network and open connection
For TCP:
```python
conn = connections.TCPConnection({
    'ip': '10.100.3.231',
    'port': 502
})
conn.open_connection(timeout=10)
```
For COM:
```python
conn = connections.COMConnection({
    'COM': 'COM1',
    'baudrate': 115200,
    'parity': serial.PARITY_NONE,
    'bytesizes': serial.EIGHTBITS,
    'stopbits': serial.STOPBITS_ONE
})
conn.open_connection(timeout=10)
```

Create class for modbus protocol.
For Modbus TCP:
```python
mb = modbusTCP_client.TSMbTCPClient()
```
For Modbus RTU:
```python
mb = modbusRTU_client.TSMbRTUClient()
```
If you need Modbus RTU protocol via TCP connection you have to create TCP connection class and TSMbRTUClient for protocol.
Use functions `execute` (for single request) and `execute_ext` (for several requests) to communicate with slave devices. How to use these functions, see the examples below or in the repository.

# Examples 1: Send single request to the device
```python
data = mb.execute(conn, function=const.READ_INPUT_REGISTERS, device_address=1, start_address=0, regs_quantity=10)
```
Response of this function is values list of readed registers. If it is write modbus function - result is empty set.
You can give more information about request. There is ts_last_request param in mb class. You can do:
```python
print(str(data) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
print(str(mb.ts_last_request) + ': ' + str(mb.ts_last_request['response_time']) + ' мс')
```
Result is:
```sh
(7480, 3, 3, 3, 0, 0, 0, 0, 0, 0): 39.68095779418945 мс
{'error': 0, 'function': 4, 'device_address': 1, 'start_address': 0, 'regs_quantity': 10, 'request': b'\x00\x01\x00\x00\x00\x06\x01\x04\x00\x00\x00\n', 'response': b'\x00\x01\x00\x00\x00\x17\x01\x04\x14\x1d8\x00\x03\x00\x03\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 'response_time': 39.68095779418945, 'values': [], 'data': (7480, 3, 3, 3, 0, 0, 0, 0, 0, 0)}: 39.68095779418945 мс
```
Param `ts_last_request` has fields:
```python
        self.ts_last_request = {
                            'error': 0,            # Modbus Error Code
                            'function': 0,         # Request function code
                            'device_address': 0,   # Device address
                            'start_address': 0,    # Start Address
                            'regs_quantity': 0,    # Quantity of registers
                            'request': b'',        # Submitted request in hexadecimal format
                            'response': b'',       # Response in hexadecimal format
                            'response_time': 0.0,  # Response time of request
                            'values': [],          # Values (for write modbus functions)
                            'data': []             # Data (for read modbus functions)
        }
```
# Examples 2: Send single command to the device
```python
data = mb.execute(conn, 
                function=const.WRITE_MULTIPLE_REGISTERS, 
                device_address=1, 
                start_address=500, 
                values=[1, 2, 3])
```
TS_Modbus will write as many values as are transferred in the value list

# Examples 3: Send several requests to the device
You can send several comands by one function. This function is `execute_ext`:
```python
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
```
The result of this function is an array of arrays with a list of values for each request. Params of all requests saved in `ts_requests_ext` field.
```python
print(result)
print(mb.ts_requests_ext)
```
```sh
[(0, 0, 0), [], (1, 2, 3), []]
[{'error': 0, 'function': 16, 'device_address': 1, 'start_address': 12300, 'regs_quantity': 3, 'request': b'\x00\x07\x00\x00\x00\r\x01\x100\x0c\x00\x03\x06\x00\x00\x00\x00\x00\x00', 'response': b'\x00\x07\x00\x00\x00\x06\x01\x100\x0c\x00\x03', 'response_time': 31.81004524230957, 'values': [0, 0, 0], 'data': []}, {'error': 0, 'function': 16, 'device_address': 1, 'start_address': 12300, 'regs_quantity': 3, 'request': b'\x00\x07\x00\x00\x00\r\x01\x100\x0c\x00\x03\x06\x00\x00\x00\x00\x00\x00', 'response': b'\x00\x07\x00\x00\x00\x06\x01\x100\x0c\x00\x03', 'response_time': 31.81004524230957, 'values': [0, 0, 0], 'data': []}, {'error': 0, 'function': 16, 'device_address': 1, 'start_address': 12300, 'regs_quantity': 3, 'request': b'\x00\x07\x00\x00\x00\r\x01\x100\x0c\x00\x03\x06\x00\x00\x00\x00\x00\x00', 'response': b'\x00\x07\x00\x00\x00\x06\x01\x100\x0c\x00\x03', 'response_time': 31.81004524230957, 'values': [0, 0, 0], 'data': []}, {'error': 0, 'function': 16, 'device_address': 1, 'start_address': 12300, 'regs_quantity': 3, 'request': b'\x00\x07\x00\x00\x00\r\x01\x100\x0c\x00\x03\x06\x00\x00\x00\x00\x00\x00', 'response': b'\x00\x07\x00\x00\x00\x06\x01\x100\x0c\x00\x03', 'response_time': 31.81004524230957, 'values': [0, 0, 0], 'data': []}]
```