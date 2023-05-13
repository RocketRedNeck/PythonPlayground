import PySimpleGUI as sg
import psutil
import sys
import math
from gauge import Gauge

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

ALPHA = 1.0
THEME = 'Renogy' #'Dark purple 6 '
UPDATE_FREQUENCY_MILLISECONDS = 100 #2 * 1000


def human_size(bytes, units=(' bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')):
    """ Returns a human readable string reprentation of bytes"""
    return str(bytes) + ' ' + units[0] if bytes < 1024 else human_size(bytes >> 10, units[1:])

def main(location):
    sg.theme(THEME)
    gwidth = 800 // 4
    gheight = 480 // 4
    gsize = (gwidth, gheight)
    layout = [
        [sg.T('CPU', font='Any 20', background_color='black')],
        [sg.Graph((gwidth, gheight), (-gwidth // 2, 0), (gwidth // 2, gheight), key='-Graph-')],
        [sg.T(size=(5, 1), font='Any 20', justification='c', k='-gauge VALUE-')]] #background_color='black'


    window = sg.Window('CPU Usage Widget Square', layout, location=location, no_titlebar=True, grab_anywhere=True, margins=(0, 0), element_padding=(0, 0), alpha_channel=ALPHA, background_color='black', element_justification='c', finalize=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, enable_close_attempted_event=True)

    clock_radius = int(0.5*gwidth) #400
    gauge = Gauge(pointer_color='red', #sg.theme_text_color(), 
                  clock_color=sg.theme_text_color(), 
                  major_tick_color=sg.theme_text_color(),
                  minor_tick_color=sg.theme_input_background_color(), 
                  pointer_outer_color=sg.theme_text_color(), 
                  major_tick_start_radius=int(0.75*clock_radius), #300,
                  minor_tick_start_radius=int(0.75*clock_radius), #300, 
                  minor_tick_stop_radius=int(0.80*clock_radius), #350, 
                  major_tick_stop_radius=int(0.80*clock_radius), #350, 
                  major_tick_step=45, #30, 
                  clock_radius=clock_radius, 
                  pointer_line_width=5, 
                  pointer_inner_radius=int(0.04*clock_radius), #10, 
                  pointer_outer_radius=int(0.95*clock_radius), #300, 
                  graph_elem=window['-Graph-'])

    gauge.change(degree=0)

    while True:  # Event Loop
        cpu_percent = psutil.cpu_percent(interval=0.1)

        if gauge.change():
            new_angle = cpu_percent*180/100
            window['-gauge VALUE-'].update(f'{int(cpu_percent)}%')
            gauge.change(degree=new_angle, step=180)
            gauge.change()
        # ----------- update the graphics and text in the window ------------
        # update the window, wait for a while, then check for exit
        event, values = window.read(timeout=UPDATE_FREQUENCY_MILLISECONDS)
        if event in (sg.WIN_CLOSE_ATTEMPTED_EVENT, 'Exit'):
            sg.user_settings_set_entry('-location-', window.current_location())  # The line of code to save the position before exiting
            break
        if event == 'Edit Me':
            sg.execute_editor(__file__)
        elif event == 'Version':
            sg.popup_scrolled(__file__, sg.get_versions(), location=window.current_location(), keep_on_top=True, non_blocking=True)
    window.close()


if __name__ == '__main__':

    if len(sys.argv) > 1:
        location = sys.argv[1].split(',')
        location = (int(location[0]), int(location[1]))
    else:
        location = sg.user_settings_get_entry('-location-', (None, None))
    main(location)