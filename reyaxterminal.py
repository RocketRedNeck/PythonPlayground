import serial

ser = serial.Serial('COM9',baudrate=115200,timeout=3)  # open serial port

ser.write(b'AT+ADDRESS?\r\n')
line = ser.readline()   # read a '\n' terminated line
print(f'Response = {line}')

while True:
    line = ser.readline()   # read a '\n' terminated line
    print(f'Received = {line}')
    msg = f'ACK = "{line}"'
    cmd = f'AT+SEND=101,{len(msg)},{msg}\r\n'
    ser.write(bytearray(cmd,'utf-8'))
    line = ser.readline()
    print(f'Response = {line}')

ser.close()

