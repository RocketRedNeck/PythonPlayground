# -*- coding: utf-8 -*-
"""
Created on Sat May 28 08:54:43 2016

@author: mtkessel
"""

import tkinter as tk
from tkinter import scrolledtext as st

import threading
import time

master = tk.Tk() 
master.title('Counting Seconds') 

button = tk.Button(master, text='Stop', bg='pink', width=10, command=master.destroy) 
button.grid(row = 0)

w = tk.Canvas(master, width=40, height=60) 
w.grid(row = 1) 
canvas_height=20
canvas_width=200
y = int(canvas_height / 2) 
w.create_line(0, y, canvas_width, y )

var1 = tk.IntVar() 
c1 = tk.Checkbutton(master, text='male', variable=var1)
c1.grid(row=2, sticky=tk.W) 

var2 = tk.IntVar() 
c2 = tk.Checkbutton(master, text='female', variable=var2)
c2.grid(row=3, sticky=tk.W)

tk.Label(master, text='First Name').grid(row=4) 
tk.Label(master, text='Last Name').grid(row=5) 
e1 = tk.Entry(master) 
e2 = tk.Entry(master) 
e1.grid(row=4, column=1) 
e2.grid(row=5, column=1)

frame = tk.Frame(master) 
frame.grid(row=6)
bottomframe = tk.Frame(master)
bottomframe.grid(row=7)
redbutton = tk.Button(frame, text = 'Red', fg ='red') 
redbutton.pack( side = tk.LEFT) 
greenbutton = tk.Button(frame, text = 'Brown', fg='brown') 
greenbutton.pack( side = tk.LEFT ) 
bluebutton = tk.Button(frame, text ='Blue', fg ='blue') 
bluebutton.pack( side = tk.LEFT ) 
blackbutton = tk.Button(bottomframe, text ='Black', fg ='black') 
blackbutton.pack( side = tk.BOTTOM) 

w = tk.Label(bottomframe, text='GeeksForGeeks.org!') 
w.pack() 

Lb = tk.Listbox(master) 
Lb.insert(1, 'Python') 
Lb.insert(2, 'Java') 
Lb.insert(3, 'C++') 
Lb.insert(4, 'Any other') 
Lb.grid(row=8)

# Obsolete and not a good practice, use regular menu instead
# mb =  tk.Menubutton ( master, text = 'GfGMenu') 
# mb.grid(row=8, column = 1)
# mb.menu  =  tk.Menu ( mb, tearoff = 0 ) 
# mb['menu']  =  mb.menu 
# cVar  = tk.IntVar() 
# aVar = tk.IntVar() 
# mb.menu.add_checkbutton ( label ='Contact', variable = cVar ) 
# mb.menu.add_checkbutton ( label = 'About', variable = aVar ) 
# mb.grid(row=8,column=1) 

menu = tk.Menu(master) 
master.config(menu=menu) 
filemenu = tk.Menu(menu) 
menu.add_cascade(label='File', menu=filemenu) 
filemenu.add_command(label='New') 
filemenu.add_command(label='Open...') 
filemenu.add_separator() 
filemenu.add_command(label='Exit', command=master.destroy) 
helpmenu = tk.Menu(menu) 
menu.add_cascade(label='Help', menu=helpmenu) 
helpmenu.add_command(label='About') 

ourMessage ='This is our Message'
messageVar = tk.Message(master, text = ourMessage) 
messageVar.config(bg='lightgreen') 
messageVar.grid(row=0, column=1)

v = tk.IntVar() 
tk.Radiobutton(master, text='GfG', variable=v, value=1).grid(row=2, column=1)
tk.Radiobutton(master, text='MIT', variable=v, value=2).grid(row=3, column=1)

w = tk.Scale(master, from_=0, to=42) 
w.grid(row=8,column=1) 
w = tk.Scale(master, from_=0, to=200, orient=tk.HORIZONTAL) 
w.grid(row=9,column=1)

newframe = tk.Frame(master)
newframe.grid(row=8, column=3)
scrollbar = tk.Scrollbar(newframe) 
scrollbar.pack( side = tk.RIGHT, fill = tk.Y ) 
mylist = tk.Listbox(newframe, yscrollcommand = scrollbar.set ) 
for line in range(100): 
   mylist.insert(tk.END, 'This is line number' + str(line)) 
mylist.pack( side = tk.LEFT, fill = tk.BOTH ) 
scrollbar.config( command = mylist.yview ) 

T = tk.Text(master, height=2, width=30) 
T.grid(row=10)
T.insert(tk.END, 'GeeksforGeeks\nBEST WEBSITE\n') 

w = tk.Spinbox(master, from_ = 0, to = 10) 
w.grid(row=10,column=1)

lblText = st.ScrolledText(master,
                      bg='white',
                      relief=tk.GROOVE,
                      height=10,
                      #width=400,
                      font='TkFixedFont',)
lblText.grid(row = 11,column = 0, sticky=tk.N+tk.S+tk.E+tk.W)
lblText.config(background="light grey", foreground="black",
                font='consolas 14 bold', wrap='word')

def tick(name):
    i = 0
    while (True):
        try:
            lblText.insert(tk.END, str(i)+'\n')
            lblText.yview(tk.END)
            i+=1
            time.sleep(0.1)
        except Exception as e:
            if 'main thread is not in main loop' in repr(e):
                break
            else:
                raise e

x = threading.Thread(target=tick, args=(1,))
x.start()

def _delete_window():
    print("delete_window")
    try:
        master.destroy()
    except:
        pass

def _destroy(event):
    print("destroy")

master.protocol("WM_DELETE_WINDOW", _delete_window)
#master.bind("<Destroy>", _destroy)

master.mainloop() 
