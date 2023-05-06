import os

#https://pypi.org/project/PySimpleGUI/
#https://realpython.com/pysimplegui-python/
import PySimpleGUI as sg

import PIL.Image
from datetime import datetime
import time

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from matplotlib import figure, pyplot

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

top_frame = [
    [sg.Text('FAULT : 0000', size=15, key='FAULT'), 
     sg.Text('\u219100000 / \u219300000', size=21, key='CHARGE COUNT'), 
     sg.Text('HH:YY::SS', key='TIME')
    ]
]

charge_power_frame = [
        [sg.Text('DEACTIVATED', font=font_medsmall, key='CHARGING STATE')],
        [sg.Text('000',font=font_large, enable_events=True, key='CHARGING POWER'), sg.Text('W')],    
]
battery_capacity_frame = [
        [sg.Text('BATTERY',font=font_medsmall)],
        [sg.Text('000', font=font_large, enable_events=True, key='BATTERY CAPACITY'), sg.Text('%')],
]
battery_VA_frame = [
        [sg.Text('BATTERY', font=font_medsmall)],
        [sg.Text('00.0', font=font_medlarge, enable_events=True, key='BATTERY VOLTAGE'), sg.Text('V')],
        [sg.Text('00.0', font=font_medlarge, enable_events=True, key='BATTERY CURRENT'), sg.Text('A')],
]

power_frame = [
    sg.Column(charge_power_frame, element_justification='center'),
    sg.Column(battery_capacity_frame, element_justification='center'),
    sg.Column(battery_VA_frame, element_justification='center'),
]

canvas_frame = [
    [sg.Canvas(key="CANVAS", pad=(0,0))]
]

temperature_frame = [
        [sg.Text('BATTERY', size=10, font=font_medsmall, justification='left'),    sg.Text('00.0', font=font_medsmall, enable_events=True, key='BATTERY TEMPERATURE'),    sg.Text('C', font=font_medsmall)],
        [sg.Text('CONTROLLER', size=10, font=font_medsmall, justification='left'), sg.Text('00.0', font=font_medsmall, enable_events=True, key='CONTROLLER TEMPERATURE'), sg.Text('C', font=font_medsmall)],
        [sg.Text('PICO', size=10, font=font_medsmall, justification='left'),       sg.Text('00.0', font=font_medsmall, enable_events=True, key='PICO TEMPERATURE'),       sg.Text('C', font=font_medsmall)],
    ]

panel_VA_frame = [
        [sg.Text('PANEL', font=font_medsmall)],
        [sg.Text('00.0', font=font_medlarge, enable_events=True, key='PANEL VOLTAGE'), sg.Text('V')],
        [sg.Text('00.0', font=font_medlarge, enable_events=True, key='PANEL CURRENT'), sg.Text('A')],
]

middle_frame = [
    sg.Column(canvas_frame, size=(330,160), element_justification='left'),
    sg.Column(temperature_frame, size=(212,85), element_justification='center'),
    sg.Column(panel_VA_frame, element_justification='center'),
]

bottom_frame = [
    [sg.Button(key='QUIT', button_color=invisible, image_filename='img_small.png', border_width=0),
     sg.Text('MODEL No. ----------------', size=28, key='MODEL No.'),
     sg.Text('--------------------', size=20, justification='right', key='Com State'),
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
window = sg.Window('Renogy Link', layout, margins=(10, 10), font = font_default, location=(0,0), size=(800,480), keep_on_top=True).Finalize() # Resizing not working right

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
    'CHARGING POWER' : None,
    'BATTERY CAPACITY' : None,
    'BATTERY VOLTAGE' : None,
    'BATTERY CURRENT' : None,
    'BATTERY TEMPERATURE' : None,
    'CONTROLLER TEMPERATURE' : None,
    'PICO TEMPERATURE' : None,
    'PANEL VOLTAGE' : None,
    'PANEL CURRENT' : None,
}

fig = figure.Figure(figsize=(3.5, 1.6), dpi=100)
t = np.arange(0, np.pi, .01)
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

draw_figure(window["CANVAS"].TKCanvas, fig)

dt = 0.01
nextTime = time.perf_counter() + dt
while True:
    now = datetime.today()
    
    window['TIME'].update(f'{now.hour:02d}:{now.minute:02d}:{now.second:02d}  {dayname[now.weekday()]} {now.day:02d}-{monname[now.month]}-{now.year}')
    
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
                break
    elif event in plotables:
        print(event)
            
window.close()