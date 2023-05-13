import os
import platform

#https://pypi.org/project/PySimpleGUI/
#https://realpython.com/pysimplegui-python/
import PySimpleGUI as sg

from gauge import Gauge
from datetime import datetime
import time

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from matplotlib import figure, pyplot

import serial
import threading

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

matplotlib.use("TkAgg")

# Add new theme colors and settings
bg_color = '#e8a202'
light_bg_color = '#FFcc66'
sg.LOOK_AND_FEEL_TABLE['Renogy'] = {
    'BACKGROUND': bg_color,
    'TEXT': '#000000',
    'INPUT': '#FFcc66',
    'TEXT_INPUT': '#000000',
    'SCROLL': '#99cc99',
    'BUTTON': ('#000000', light_bg_color),
    'PROGRESS': ('#0000ff', light_bg_color),
    'BORDER': 1, 'SLIDER_DEPTH': 0, 
    'PROGRESS_DEPTH': 0
    }
theme = sg.theme('Renogy')
invisible = (sg.theme_background_color(), sg.theme_background_color())

#sg.popup_get_text('Renogy theme looks like this') 

# 2191 and 2193
font_name = 'Liberation Mono'
font_small = (font_name, 7,)
font_medsmall = (font_name, 13)
font_medium = (font_name, 15)
font_medlarge = (font_name, 38)
font_large = (font_name, 96)

font_default = font_medium

window_size=(800,480)
window_width = window_size[0]
window_height = window_size[1]

top_frame = [
    [sg.Text('FAULT:'), 
     sg.Text('0000', key='FAULT'), 
     sg.Text('HH:YY::SS', key='TIME')
    ]
]

gwidth = window_width // 4
gheight = window_height // 4
battery_capacity_frame = [
        [sg.Text('BATTERY',font=font_medsmall)],
        [sg.Graph((gwidth, gheight), (-gwidth // 2, 0), (gwidth // 2, gheight), key='-Graph-')],
        [sg.Text('E',font=font_medium), 
         sg.Text('-----', font=font_small, key='DISCHARGE COUNT'), 
         sg.Text('---', font=font_medium, enable_events=True, key='BATTERY CAPACITY'), sg.Text('%'),
         sg.Text('-----', font=font_small, key='CHARGE COUNT'),
         sg.Text('F',font=font_medium)
        ]
]

charge_frame = [
        [sg.Text('CHARGE OFF', font=font_medsmall, key='CHARGING STATE')],
        [sg.Text(' --.-', font=font_medium, enable_events=True, key='BATTERY VOLTAGE'), sg.Text('V')],
        [sg.Text('--.--', font=font_medium, enable_events=True, key='CHARGING CURRENT'), sg.Text('A')],
        [sg.Text('  ---',font=font_medium, enable_events=True, key='CHARGING POWER'), sg.Text('W')],    
        [sg.Text('  ---',font=font_medium, enable_events=True, key='CHARGE'), sg.Text('AH')],    
]

load_frame = [
        [sg.Text('LOAD', font=font_medsmall), sg.Text('OFF',font=font_medsmall, key='LOAD STATE')],
        [sg.Text(' --.-', font=font_medium, enable_events=True, key='LOAD VOLTAGE'), sg.Text('V')],
        [sg.Text('--.--', font=font_medium, enable_events=True, key='LOAD CURRENT'), sg.Text('A')],
        [sg.Text('  ---',font=font_medium, enable_events=True, key='LOAD POWER'), sg.Text('W')],    
        [sg.Text('  ---',font=font_medium, enable_events=True, key='DISCHARGE'), sg.Text('AH')],    
]

panel_frame = [
        [sg.Text('PANEL', font=font_medsmall)],
        [sg.Text(' --.-', font=font_medium, enable_events=True, key='PANEL VOLTAGE'), sg.Text('V')],
        [sg.Text('--.--', font=font_medium, enable_events=True, key='PANEL CURRENT'), sg.Text('A')],
]

temperature_frame = [
        [sg.Text('TEMPERATURE', font=font_medsmall)],
        [sg.Text('AMBI', font=font_medsmall, justification='left'),    sg.Text('----', font=font_medsmall, enable_events=True, key='AMBIENT TEMPERATURE'),    sg.Text('C', font=font_medsmall)],
        [sg.Text('CTRL', font=font_medsmall, justification='left'), sg.Text('----', font=font_medsmall, enable_events=True, key='CONTROLLER TEMPERATURE'), sg.Text('C', font=font_medsmall)],
        [sg.Text('PICO', font=font_medsmall, justification='left'),       sg.Text('----', font=font_medsmall, enable_events=True, key='PICO TEMPERATURE'),       sg.Text('C', font=font_medsmall)],
        [sg.Text('BAT1', font=font_medsmall, justification='left'),       sg.Text('----', font=font_medsmall, enable_events=True, key='BAT1 TEMPERATURE'),       sg.Text('C', font=font_medsmall)],
        [sg.Text('BAT2', font=font_medsmall, justification='left'),       sg.Text('----', font=font_medsmall, enable_events=True, key='BAT2 TEMPERATURE'),       sg.Text('C', font=font_medsmall)],
        [sg.Text('BAT3', font=font_medsmall, justification='left'),       sg.Text('----', font=font_medsmall, enable_events=True, key='BAT3 TEMPERATURE'),       sg.Text('C', font=font_medsmall)],
]

power_frame = [
    sg.Column(battery_capacity_frame, element_justification='center'),
    sg.Column(charge_frame, element_justification='center'),
    sg.Column(load_frame, element_justification='center'),
    sg.Column(panel_frame, element_justification='center'),
    sg.Column(temperature_frame, element_justification='center'),
]

canvas_frame = [
    [sg.Canvas(key="CANVAS", pad=(0,0))]
]


middle_frame = [
    sg.Column(canvas_frame, element_justification='left')
]

bottom_frame = [
    [sg.Button(key='QUIT', button_color=invisible, image_filename='img_small.png', border_width=0),
     sg.Text('MODEL No. ----------------', size=28, key='MODEL No.'),
     sg.Text('--------------------', size=20, justification='right', key='COM STATE'),
     sg.Text('000000000', key='FRAME COUNT')
    ]
]

layout = [
    [top_frame],
    [sg.HSep()],
    [power_frame],
    #[sg.HSep()],
    [middle_frame],
    [sg.HSep()],
    [bottom_frame]
]
window = sg.Window('Renogy Link', layout, font = font_default, location=(0,0), size=(800,480), keep_on_top=True).Finalize()
if platform.system() == 'Linux':
    window.Maximize()

clock_radius = int(0.5*gwidth)
min_angle = 5
max_angle = 175
ang_range = max_angle - min_angle
gauge = Gauge(start_angle=min_angle, stop_angle=max_angle,
              pointer_color='red',
              clock_color=sg.theme_text_color(), 
              major_tick_color=sg.theme_text_color(),
              minor_tick_color=sg.theme_input_background_color(), 
              pointer_outer_color=sg.theme_text_color(), 
              major_tick_start_radius=int(0.75*clock_radius),
              minor_tick_start_radius=int(0.75*clock_radius),
              minor_tick_stop_radius=int(0.80*clock_radius),
              major_tick_stop_radius=int(0.80*clock_radius), 
              major_tick_step=45,
              clock_radius=clock_radius, 
              pointer_line_width=5, 
              pointer_inner_radius=int(0.04*clock_radius), 
              pointer_outer_radius=int(0.95*clock_radius), 
              graph_elem=window['-Graph-'])

gauge.change(degree=min_angle)
gauge.change()

dayname = {
    0 : 'MON',
    1 : 'TUE',
    2 : 'WED',
    3 : 'THU',
    4 : 'FRI',
    5 : 'SAT',
    6 : 'SUN'
}

monname = {
    1 : 'JAN',
    2 : 'FEB',
    3 : 'MAR',
    4 : 'APR',
    5 : 'MAY',
    6 : 'JUN',
    7 : 'JUL',
    8 : 'AUG',
    9 : 'SEP',
    10 : 'OCT',
    11 : 'NOV',
    12 : 'DEC'
}

plotables = {
    'AMBIENT TEMPERATURE' : None,
    'BATTERY CAPACITY' : None,
    'BATTERY VOLTAGE' : None,
    'CHARGING CURRENT' : None,
    'CHARGING POWER' : None,
    'CHARGE' : None,
    'CONTROLLER TEMPERATURE' : None,
    'LOAD CURRENT' : None,
    'LOAD POWER' : None,
    'LOAD VOLTAGE' : None,
    'DISCHARGE' : None,
    'PANEL VOLTAGE' : None,
    'PANEL CURRENT' : None,
    'PICO TEMPERATURE' : None,
}

fig = figure.Figure(figsize=(8.0, 1.6), dpi=100)
t = np.arange(0, np.pi, np.pi/24)
ax = fig.add_subplot(111)
y = np.abs(np.sin(2 * np.pi * t))
line, = ax.plot(t, y)
ax.margins(0)
ax.grid()
ax.get_xaxis().set_ticklabels([]) #set_visible(True)
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def runRenogyDisplay():
    global window
    draw_figure(window["CANVAS"].TKCanvas, fig)

    dt = 0.01
    nextTime = time.perf_counter() + dt
    while True:
        now = datetime.today()
        
        window['TIME'].update(f'{now.hour:02d}:{now.minute:02d}:{now.second:02d}  {dayname[now.weekday()]} {now.day:02d}-{monname[now.month]}-{now.year}')
        gauge.step()
        
        if time.perf_counter() > nextTime:
            nextTime = nextTime + dt

            line.set_ydata(y + np.random.random(len(t)))
            fig.canvas.draw()
            fig.canvas.flush_events()
            ax.relim() #scale the y scale
            ax.autoscale_view() #scale the y scale
        
        event, values = window.read(timeout=int(dt*1000))
        
        # End program if user closes window or
        # presses the OK button
        if event == "QUIT" or event == sg.WIN_CLOSED:
            answer = sg.popup_yes_no('Reboot?', 'Would you like to reboot?', keep_on_top=True)
            if answer == 'Yes':
                try:
                    os.system('sudo reboot')
                except Exception as e:
                    print(e)
                    pass
                break
            else:
                answer = sg.popup_yes_no('Quit?', 'Would you like to quit, instead?', keep_on_top=True)
                if answer == 'Yes':
                    window.close()
                    exit()
        elif event in plotables:
            print(event)
  
decoder = {
   0 : ("BATTERY CAPACITY", "%", 1.0),
   1 : ("BATTERY VOLTAGE", "V", 0.1),
   2 : ("CHARGING CURRENT", "A", 0.01),
   3 : ("CONTROLLER TEMPERATURE", "C", 1.0, "BATTERY TEMPERATURE", "C", 1.0, True),
  35 : ("PICO TEMPERATURE", "C", 1.0),
   4 : ("LOAD VOLTAGE", "V", 0.1),
   5 : ("LOAD CURRENT", "A", 0.01),
   6 : ("LOAD POWER", "W", 1.0),
   7 : ("PANEL VOLTAGE", "V", 0.1),
   8 : ("PANEL CURRENT", "A", 0.01),
   9 : ("CHARGING POWER", "W", 1.0),
  17 : ("CHARGE", "AH", 1.0),
  18 : ("DISCHARGE", "AH", 1.0),
  22 : ("DISCHARGE COUNT", "-", 1.0),
  23 : ("CHARGE COUNT", "-", 1.0),
  32 : ("CHARGING STATE", "-", 1.0, False, "Enum", 
        {0:"CHARGE OFF",
         1:"CHARGE ACTIVATED",
         2:"CHARGE MPPT",
         3:"CHARGE EQUALIZING",
         4:"CHARGE BOOST",
         5:"CHARGE FLOAT",
         6:"CHARGE LIMITING",
         32768:"CHARGE OFF",
         32769:"CHARGE ACTIVATED",
         32770:"CHARGE MPPT",
         32771:"CHARGE EQUALIZING",
         32772:"CHARGE BOOST",
         32773:"CHARGE FLOAT",
         32774:"CHARGE LIMITING"
         }
       ),
  33 : ("FAULT", "-", 1.0, False, "Mask",
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
            return
    else:
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
    
def renogyDataLoop():
    ser = connect()

    global window
    loopNames = {
        1 : 'MODEL No.',
        2 : 'SERIAL_NO',
        0 : 'DATA     ',
        9 : 'ERROR    '
    }
    timeoutCount = 0
    frameCount = 0
    while True:
        try:
            while (True):
                try:
                    line = ser.readline().decode("utf-8")
                    break
                except Exception as e:
                    window['COM STATE'].update('USB-TTL DISCONNECTED')
                    if ser is not None:
                        ser.close()
                    ser = connect(False)
                    
            if len(line) > 0:
                frameCount = frameCount + 1
                window['FRAME COUNT'].update(f'{frameCount:9d}')
                window['COM STATE'].update('')
                timeoutCount = 0
                atParts = line.split(',')
                if 1 < len(atParts):
                    loopParts = atParts[2].split(':')
                    if 0 < len(loopParts):
                        index = int(loopParts[0])
                        if index is not None:
                            data = loopParts[1]
                            element = window.find_element(loopNames[index].strip(),silent_on_error=True)
                            if element is not None and not isinstance(element, sg.ErrorElement):
                                element.update(data.strip())

                            if index == 9:
                                window['COM STATE'].update('RS-232 DISCONNECTED')
                            elif index == 0:
                                for key, value in decoder.items():
                                    k = 4*key
                                    if len(value) == 3:
                                        x = int(data[k:k+4],16)
                                        x = x * value[2]
                                        if value[1] == '%':
                                            s = f'{int(x):3d}'
                                        elif value[1] == 'W':
                                            s = f'{int(x):5d}'
                                        elif value[1] == 'V':
                                            s = f'{x:5.1f}'
                                        elif value[1] == 'A':
                                            s = f'{x:5.2f}'
                                        elif value[1] == 'AH':
                                            s = f'{int(x):5d}'
                                        elif value[1] == 'C':
                                            s = f'{x:4.0f}'
                                        elif value[1] == '-':
                                            s = f'{int(x):05d}'
                                        else:
                                            s = f'{x:4.1f}'
                                        element = window.find_element(value[0].strip(), silent_on_error=True)
                                        if element is not None and not isinstance(element, sg.ErrorElement):
                                            element.update(s)

                                        if value[0] == 'BATTERY CAPACITY':
                                            gauge.change(degree=int(x/100)*ang_range+min_angle, step=10)

                                    elif len(value) == 6:
                                        if value[3] == True:
                                            s = 8
                                        else:
                                            s = 4
                                        d = data[k:k+s]
                                        if "Enum" == value[4]:
                                            x = int(data[k:k+s],16)
                                            if x in value[5]:
                                                d = value[5][x]
                                        element = window.find_element(value[0].strip(), silent_on_error=True)
                                        if element is not None and not isinstance(element, sg.ErrorElement):
                                            element.update(f'{d}')
                                        if value[0] == 'CHARGING STATE':
                                            if x >= 32768:
                                                load_state = 'ON'
                                            else:
                                                load_state = 'OFF'
                                                
                                            element = window.find_element('LOAD STATE', silent_on_error=True)
                                            if element is not None and not isinstance(element, sg.ErrorElement):
                                                element.update(f'{load_state}')
                                                
                                            
                                    elif len(value) == 7:
                                        x = int(data[k:k+2],16)
                                        x = x * value[2]
                                        if value[1] == 'C':
                                            s = f'{x:4.0f}'
                                        else:
                                            s = f'{x:4.1f}'                                        
                                        element = window.find_element(value[0].strip(), silent_on_error=True)
                                        if element is not None and not isinstance(element, sg.ErrorElement):
                                            element.update(f'{s}')
                                        x = int(data[k+2:k+4],16)
                                        x = x * value[5]
                                        if value[1] == 'C':
                                            s = f'{x:4.0f}'
                                        else:
                                            s = f'{x:4.1f}'                                        
                                        element = window.find_element(value[3].strip(), silent_on_error=True)
                                        if element is not None and not isinstance(element, sg.ErrorElement):
                                            element.update(f'{s}')
                                        
            else:
                frameCount = frameCount + 1
                window['FRAME COUNT'].update(f'{frameCount:9d}')
                timeoutCount = timeoutCount + 1
                window['COM STATE'].update(f'TIMEOUT {timeoutCount}  ')
        except Exception as e:
            print(e)
            pass    
        
x = threading.Thread(target=renogyDataLoop)
x.setDaemon(True)
x.start()

runRenogyDisplay()

