from getch import getch
import serial
import time

s = serial.Serial(port='/dev/ttyUSB0',
                  baudrate = 115200,
                  parity = serial.PARITY_ODD,
                  stopbits = serial.STOPBITS_ONE,
                  timeout = 0.1)

while True:
    try:
        c = getch()
        x = bytes(c,'utf-8')
        s.write(x)
        if chr(3) == c:
            break
        print(c,flush=True, end='' if chr(13) != c else '\n')
    except Exception as e:
        print(f'{repr(e)} : Running in Thonny?')
