import serial

ser = serial.Serial('COM3',baudrate=115200,timeout=3)  # open serial port

ser.write(b'AT+ADDRESS?\r\n')
line = ser.readline()   # read a '\n' terminated line
print(f'Response = {line}')

while True:
    line = ser.readline()   # read a '\n' terminated line
    print(f'Response = {line}')

ser.close()

