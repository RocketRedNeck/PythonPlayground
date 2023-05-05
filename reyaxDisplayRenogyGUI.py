import os
import serial
from sys import platform
import time

#https://pypi.org/project/PySimpleGUI/
#https://realpython.com/pysimplegui-python/
import PySimpleGUI as sg

decoder = {
   0 : ("BATTERY_CAPACITY", "%", 1.0),
   1 : ("BATTERY_VOLTAGE", "V", 0.1),
   2 : ("CHARGING_CURRENT", "A", 0.01),
   3 : ("TEMPERATURE_CNTLR", "C", 1.0, "TEMPERATURE_BATT", "C", 1.0, True),
  35 : ("TEMPERATURE_PICO", "C", 1.0),
   4 : ("STREET_LIGHT_VOLTAGE", "V", 0.1),
   5 : ("STREET_LIGHT_CURRENT", "A", 0.01),
   6 : ("STREET_LIGHT_POWER", "W", 1.0),
   7 : ("SOLAR_PANEL_VOLTAGE", "V", 0.1),
   8 : ("SOLAR_PANEL_CURRENT", "A", 0.01),
   9 : ("CHARGING_POWER", "W", 1.0),
  #10 : ("LIGHT_ON_OFF_COMMAND", "-", 1.0),
  11 : ("BATTERY_MIN_VOLTAGE_OF_DAY", "V", 0.1),
  12 : ("BATTERY_MAX_VOLTAGE_OF_DAY", "V", 0.1),
  13 : ("MAX_CHARGING_CURRENT_OF_DAY", "A", 0.01),
  14 : ("MAX_DISCHARGING_CURRENT_OF_DAY", "A", 0.01),
  15 : ("MAX_CHARGING_POWER_OF_DAY", "W", 1.0),
  16 : ("MAX_DISCHARGING_POWER_OF_DAY", "W", 1.0),
  17 : ("CHARGING_OF_DAY", "AH", 1.0),
  18 : ("DISCHARGING_OF_DAY", "AH", 1.0),
  19 : ("POWER_GENERATION_OF_DAY", "WH", 0.1),
  20 : ("POWER_CONSUMPTION_OF_DAY", "WH", 0.1),
  21 : ("TOTAL_OPERATING_DAYS", "-", 1.0),
  22 : ("TOTAL_BATTERY_OVER_DISCHARGES", "-", 1.0),
  23 : ("TOTAL_BATTERY_FULL_CHARGES", "-", 1.0),
  24 : ("TOTAL_CHARGING", "AH", 1.0, True),
  26 : ("TOTAL_DISCHARGING", "AH", 1.0, True),
  28 : ("CUMULATIVE_POWER_GENERATION", "WH", 0.1, True),
  30 : ("CUMULATIVE_POWER_CONSUMPTION", "WH", 0.1, True),
  32 : ("CHARGING_STATE", "-", 1.0, False, "Enum", 
        {0:"DEACTIVATED",
         1:"ACTIVATED",
         2:"MPPT",
         3:"EQUALIZING",
         4:"BOOST",
         5:"FLOAT",
         6:"CURRENT LIMITING (OVERPOWER)"
         }
       ),
  33 : ("CONTROLLER_FAULT_WARNING", "-", 1.0, False, "Mask",
        {30:"CHARGE MOS SHORT",
         29:"ANTI-REVERSE MOS SHORT",
         28:"SOLAR PANEL REVERSED",
         27:"SOLAR PANEL WORKING POINT OVER-VOLTAGE",
         26:"SOLAR PANEL COUNTER-CURRENT",
         25:"PHOTOVOLTAIC INPUT SIDE OVER VOLTAGE",
         24:"PHOTOVOLTAIC INPUT SIDE SHORT",
         23:"PHOTOVOLTAIC INPUT OVERPOWER",
         22:"AMBIENT TEMPERATURE TOO HIGH",
         21:"CONTROLLER TEMPERATURE TOO HIGH",
         20:"LOAD OVER-POWER/CURRENT",
         19:"LOAD SHORT",
         18:"BATTERY UNDER-VOLTAGE",
         17:"BATTERY OVER-VOLTATE",
         16:"BATTERY OVER-DISCHARGE"
        }
       )
}


def connect(exitOnFail = True):
    coms = [
        '/dev/ttyUSB0',
        '/dev/ttyUSB1',
        '/dev/ttyUSB2',
        '/dev/ttyUSB3',
        'COM5'
    ]
    ser = None
    for com in coms:
        try:
            print(f'trying {com}')
            ser = serial.Serial(com,baudrate=115200,timeout=5)  # open serial port
            print(f'Found {com}')
            ser.write(b'AT\r\n')
            line = ser.readline().decode('utf-8')   # read a '\n' terminated line
            print(line)
            if line == "+OK\r\n":
                print(f'Connected to {com}')
                break
            else:
                ser.close()
        except Exception as e:
            pass

    if ser is None:
        print('None of the expected COM ports were found')
        if exitOnFail:
            exit()

    ser.write(b'AT+ADDRESS=101\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')
    ser.write(b'AT+ADDRESS?\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')
    ser.write(b'AT+PARAMETER?\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')
    ser.write(b'AT+PARAMETER=11,8,1,4\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')
    ser.write(b'AT+PARAMETER?\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')
    ser.write(b'AT+BAND=915000000\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')
    ser.write(b'AT+BAND?\r\n')
    line = ser.readline().decode('utf-8')   # read a '\n' terminated line
    print(f'{line}')

    return ser

ser = connect()

sg.theme('system default')
layout_col1 = [
    [sg.Text(size=(50,1), key='-FRAME-')],
    [sg.Text(size=(50,1), key='-BATTERY_CAPACITY-')],
    [sg.Text(size=(50,1), key='-BATTERY_VOLTAGE-')],
    [sg.Text(size=(50,1), key='-CHARGING_CURRENT-')],
    [sg.Text(size=(50,1), key='-CHARGING_POWER-')],
    [sg.Text(size=(50,1), key='-CHARGING_STATE-')],
    [sg.Text(size=(50,1), key='-SOLAR_PANEL_VOLTAGE-')],
    [sg.Text(size=(50,1), key='-SOLAR_PANEL_CURRENT-')],
    [sg.Text(size=(50,1), key='-TEMPERATURE_CNTLR-')],
    [sg.Text(size=(50,1), key='-TEMPERATURE_BATT-')],
    [sg.Text(size=(50,1), key='-TEMPERATURE_PICO-')],
    [sg.Text(size=(50,1), key='-CONTROLLER_FAULT_WARNING-')]
]

layout_col2 = [
    [sg.Text(size=(50,1), key='-MODEL-')],
    [sg.Text(size=(50,1), key='-SERIAL_NO-')],
    [sg.Text(size=(50,1), key='-TOTAL_BATTERY_OVER_DISCHARGES-')],
    [sg.Text(size=(50,1), key='-TOTAL_BATTERY_FULL_CHARGES-')],
    [sg.Text(size=(50,1), key='-TOTAL_CHARGING-')],
    [sg.Text(size=(50,1), key='-CUMULATIVE_POWER_GENERATION-')],
    [sg.Text(size=(50,1), key='-CHARGING_OF_DAY-')],
    [sg.Text(size=(50,1), key='-POWER_GENERATION_OF_DAY-')]
    [[sg.Button("QUIT")], [sg.Button("RESTART")]]
]

layout = [
    [
        sg.Column(layout_col1),
        sg.VSeperator(),
        sg.Column(layout_col2),
    ]
]
font = ('Consolas', 9, "bold") #('LCD', 7, "bold")
offset = 25
window = sg.Window('Renogy Link', layout, margins=(10, 10), font = font, location=(0,0), size=(800,480), keep_on_top=True).Finalize() # Resizing not working right
window.Maximize()
# if platform == "linux" or platform == "linux2":
#     # linux
#     window.Maximize()
# elif platform == "darwin":
#     # OS X
#     pass
# elif platform == "win32":
#     # Windows...
#     pass
    
loopNames = {
    1 : 'MODEL    ',
    2 : 'SERIAL_NO',
    0 : 'DATA     ',
    9 : 'ERROR    '
}
timeoutCount = 0
frameCount = 0
while True:
    event, values = window.read(timeout=100)
    
    # End program if user closes window or
    # presses the OK button
    if event == "QUIT" or event == sg.WIN_CLOSED:
        answer = sg.popup_yes_no('Quit?', 'Are you sure?', keep_on_top=True)
        if answer == 'Yes':
            break
        
    elif event == "RESTART":
        answer = sg.popup_yes_no('You are about to reboot the system.', 'Are you OK with that?', keep_on_top=True)

        if answer == 'Yes':
            try:
                os.system('sudo reboot')
            except Exception as e:
                print(e)
                pass
    
    try:
        while (True):
            try:
                line = ser.readline().decode("utf-8")
                break
            except Exception as e:
                window['-FRAME-'].update(f'FRAME : {frameCount} (USB-TTL DISCONNECTED)')
                ser.close()
                ser = connect(False)
                
        if len(line) > 0:
            frameCount = frameCount + 1
            window['-FRAME-'].update(f'FRAME : {frameCount}')
            timeoutCount = 0
            atParts = line.split(',')
            if 1 < len(atParts):
                #print(atParts[2])
                loopParts = atParts[2].split(':')
                if 0 < len(loopParts):
                    index = int(loopParts[0])
                    if index is not None:
                        data = loopParts[1]
                        print(f'{loopNames[index]} : {data}')
                        element = window.find_element(f'-{loopNames[index].strip()}-',silent_on_error=True)
                        if element is not None and not isinstance(element, sg.ErrorElement):
                            element.update(f'{loopNames[index]} : {data.strip()}')

                        if index == 9:
                            window['-FRAME-'].update(f'FRAME : {frameCount} (RS-232 DISCONNECTED)')
                        elif index == 0:
                            for key, value in decoder.items():
                                #print(f'{key} : {value[0]} {len(value)}')
                                k = 4*key
                                if len(value) == 3:
                                    x = int(data[k:k+4],16)
                                    x = x * value[2]
                                    print(f'{key:2d} : {value[0]} = {x:.1f} {value[1]}')
                                    element = window.find_element(f'-{value[0].strip()}-', silent_on_error=True)
                                    if element is not None and not isinstance(element, sg.ErrorElement):
                                        element.update(f'{value[0]:35s} {x:.1f} {value[1]}')

                                elif len(value) == 4:
                                    x = int(data[k:k+8],16)
                                    x = x * value[2]
                                    print(f'{key:2d} : {value[0]} = {x:.1f} {value[1]}')
                                    element = window.find_element(f'-{value[0].strip()}-', silent_on_error=True)
                                    if element is not None and not isinstance(element, sg.ErrorElement):
                                        element.update(f'{value[0]:35s} {x:.1f} {value[1]}')
                                elif len(value) == 6:
                                    if value[3] == True:
                                        s = 8
                                    else:
                                        s = 4
                                    d = data[k:k+s]
                                    print(f'{key:2d} : {value[0]} = {d}')
                                    if "Enum" == value[4]:
                                        x = int(data[k:k+s])
                                        if x in value[5]:
                                            d = value[5][x]
                                    element = window.find_element(f'-{value[0].strip()}-', silent_on_error=True)
                                    if element is not None and not isinstance(element, sg.ErrorElement):
                                        element.update(f'{value[0]:35s} {d}')
                                elif len(value) == 7:
                                    x = int(data[k:k+2],16)
                                    x = x * value[2]
                                    print(f'{key:2d} : {value[0]} = {x:.1f} {value[1]}')
                                    element = window.find_element(f'-{value[0].strip()}-', silent_on_error=True)
                                    if element is not None and not isinstance(element, sg.ErrorElement):
                                        element.update(f'{value[0]:35s} {x:.1f} {value[1]}')
                                    x = int(data[k+2:k+4],16)
                                    x = x * value[5]
                                    print(f'{key:2d} : {value[3]} = {x:.1f} {value[4]}')                        
                                    element = window.find_element(f'-{value[3].strip()}-', silent_on_error=True)
                                    if element is not None and not isinstance(element, sg.ErrorElement):
                                        element.update(f'{value[3]:35s} {x:.1f} {value[4]}')
                                    
        else:
            frameCount = frameCount + 1
            window['-FRAME-'].update(f'FRAME : {frameCount} (TIMEOUT)')
            timeoutCount = timeoutCount + 1
            print(f'Timeout {timeoutCount}')
    except Exception as e:
        print(e)
        pass
            
window.close()
ser.close()

