import serial

s = serial.Serial(port='/dev/ttyUSB0',
                  baudrate = 115200,
                  parity = serial.PARITY_ODD,
                  stopbits = serial.STOPBITS_ONE,
                  timeout = 0.1)

while True:
    try:
        x = s.read(1)
        c = x.decode('utf-8')
        print(c,end= '' if c != '\r' else '\n' )
    except:
        pass