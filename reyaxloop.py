import serial

ser1 = serial.Serial('COM4',baudrate=115200,timeout=3)  # open serial port
ser2 = serial.Serial('COM5',baudrate=115200,timeout=3)  # open serial port

ser1.write(b'AT+ADDRESS?\r\n')
line = ser1.readline()   # read a '\n' terminated line
print(f'Response = {line}')

ser2.write(b'AT+ADDRESS?\r\n')
line = ser2.readline()   # read a '\n' terminated line
print(f'Response = {line}')

for i in range(10):
    msg = f'hello_{i}'
    cmd = f'AT+SEND=101,{len(msg)},{msg}\r\n'
    ser2.write(bytearray(cmd,'utf-8'))
    line = ser1.readline()   # read a '\n' terminated line
    print(f'Response = {line}')
    

ser1.close()
ser2.close()

