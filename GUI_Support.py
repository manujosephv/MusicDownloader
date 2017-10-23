#! /usr/bin/env python
#
# Support module generated by PAGE version 4.9
# In conjunction with Tcl version 8.6
#    Oct 03, 2017 10:14:04 PM


import sys
import json
import os

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

def set_Tk_var():
    
    ### LOADING THE CONFIG VARIABLES FROM FILE
    with open('config.json', 'r') as f:
        config = json.load(f)
    

    global spinbox
    spinbox = IntVar()
    global scan_folder
    scan_folder = StringVar()
    global move_folder
    move_folder = StringVar()
    global gplay
    gplay = IntVar()
    gplay.set(1)
    global todoist
    todoist = IntVar()
    todoist.set(1)
    global bb
    bb = IntVar()
    bb.set(1)
    spinbox.set(config['BILLBOARD']['MAX_SONGS'])
    scan_folder.set(os.path.join(config['DEFAULT']['ROOT'],os.path.basename(config['MUSICTOOLS']['DOWNLOAD_PATH'])))
    move_folder.set(os.path.join(config['DEFAULT']['ROOT'],'No AlbumArt'))
    global hot_100
    hot_100 = IntVar()
    hot_100.set(1)
    global hiphop
    hiphop = IntVar()
    hiphop.set(1)
    global edm
    edm = IntVar()
    edm.set(1)
    global risers
    risers = IntVar()
    risers.set(1)
    global choice
    choice = StringVar()
    choice.set('Pocket')
    global urls
    urls = StringVar()


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None

if __name__ == '__main__':
    import test
    test.vp_start_gui()

