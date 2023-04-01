import serial

ser = serial.Serial('COM5',baudrate=115200,timeout=3)  # open serial port

ser.write(b'AT+ADDRESS?\r\n')
line = ser.readline()   # read a '\n' terminated line
print(f'Response = {line}')

i = 0
while True:
    msg = f'hello_{i}'
    cmd = f'AT+SEND=101,{len(msg)},{msg}\r\n'
    ser.write(bytearray(cmd,'utf-8'))
    line = ser.readline()   # read a '\n' terminated line
    print(f'Response = {line}')
    i = i + 1

ser.close()

