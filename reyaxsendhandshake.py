import serial

ser = serial.Serial('COM5',baudrate=115200,timeout=3)  # open serial port

ser.write(b'AT+ADDRESS?\r\n')
line = ser.readline()   # read a '\n' terminated line
print(f'Response = {line}')

i = 0
while True:
    msg = f'hello_{i}'
    cmd = f'AT+SEND=102,{len(msg)},{msg}\r\n'
    print(f'{cmd}')
    ser.write(bytearray(cmd,'utf-8'))
    line = ser.readline()   # read a '\n' terminated line
    print(f'{str(line)}')
    i = i + 1
    line = ser.readline()   # read a '\n' terminated line
    print(f'{str(line)}')

ser.close()

