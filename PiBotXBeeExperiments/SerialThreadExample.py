from getch import getch
import serial
import threading
import time

s = serial.Serial(port='/dev/ttyUSB0',
                  baudrate = 115200,
                  parity = serial.PARITY_ODD,
                  stopbits = serial.STOPBITS_ONE,
                  timeout = 0.1)

def reader():
    while True:
        try:
            x = s.read(1)
            c = x.decode('utf-8')
            print(c, flush=True, end= '' if c != '\r' else '\n' )
        except:
            pass

def writer():
    while True:
        try:
            c = getch()
            x = bytes(c,'utf-8')
            s.write(x)
            print(c,flush=True, end='' if c != '\r' else '\n')
        except Exception as e:
            print(f'{repr(e)} : Running in Thonny?')

if __name__== "__main__":
    r = threading.Thread(target=reader, daemon=True)
    w = threading.Thread(target=writer, daemon=True)
    
    r.start()
    w.start()
    
    r.join()
    w.join()