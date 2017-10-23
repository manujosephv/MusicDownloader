#! /usr/bin/env python
#
# GUI module generated by PAGE version 4.9
# In conjunction with Tcl version 8.6
#    Oct 19, 2017 07:53:09 AM
import sys

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

import GUI_Support
from DownloadScripts import Spotify_to_GoogleMusic
from DownloadScripts import Billboard_to_GoogleMusic

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    GUI_Support.set_Tk_var()
    top = Playlist_Syncing (root)
    GUI_Support.init(root, top)
    root.mainloop()

w = None
def create_Playlist_Syncing(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    GUI_Support.set_Tk_var()
    top = Playlist_Syncing (w)
    GUI_Support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Playlist_Syncing():
    global w
    w.destroy()
    w = None


class Playlist_Syncing:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 
        font11 = "-family {Segoe UI} -size 9 -weight bold -slant roman"  \
            " -underline 0 -overstrike 0"

        top.geometry("600x482+650+150")
        top.title("Playlist Syncing")
        top.configure(background="#444444")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")



        self.menubar = Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)



        self.Labelframe4 = LabelFrame(top)
        self.Labelframe4.place(relx=0.05, rely=0.5, relheight=0.43
                , relwidth=0.88)
        self.Labelframe4.configure(relief=RIDGE)
        self.Labelframe4.configure(font=font11)
        self.Labelframe4.configure(foreground="#09bbf7")
        self.Labelframe4.configure(relief=RIDGE)
        self.Labelframe4.configure(text='''Move Spotify Playlist to Google Music''')
        self.Labelframe4.configure(background="#444444")
        self.Labelframe4.configure(highlightbackground="#d9d9d9")
        self.Labelframe4.configure(highlightcolor="black")
        self.Labelframe4.configure(width=530)

        self.Button4 = Button(self.Labelframe4)
        self.Button4.place(relx=0.51, rely=0.73, height=42, width=188)
        self.Button4.configure(activebackground="#d9d9d9")
        self.Button4.configure(activeforeground="#000000")
        self.Button4.configure(background="#09bbf7")
        self.Button4.configure(disabledforeground="#a3a3a3")
        self.Button4.configure(foreground="#000000")
        self.Button4.configure(highlightbackground="#d9d9d9")
        self.Button4.configure(highlightcolor="black")
        self.Button4.configure(pady="0")
        self.Button4.configure(text='''Sync Playlists''')
        self.Button4.configure(command = self.spotify)

        self.Entry1 = Entry(self.Labelframe4)
        self.Entry1.place(relx=0.4, rely=0.44, relheight=0.13, relwidth=0.57)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="#c4c4c4")
        self.Entry1.configure(selectforeground="black")
        READONLY = 'readonly'
        self.Entry1.configure(state=READONLY)
        self.Entry1.configure(textvariable=GUI_Support.urls)
        self.Entry1.configure(width=304)

        self.Label1 = Label(self.Labelframe4)
        self.Label1.place(relx=0.04, rely=0.44, height=26, width=190)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="#444444")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#ffffff")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Spotify Playlist URL''')
        self.Label1.configure(width=190)

        self.Radiobutton1 = Radiobutton(self.Labelframe4)
        self.Radiobutton1.place(relx=0.04, rely=0.2, relheight=0.18
                , relwidth=0.42)
        self.Radiobutton1.configure(activebackground="#d9d9d9")
        self.Radiobutton1.configure(activeforeground="#000000")
        self.Radiobutton1.configure(background="#444444")
        self.Radiobutton1.configure(disabledforeground="#a3a3a3")
        self.Radiobutton1.configure(foreground="#09bbf7")
        self.Radiobutton1.configure(highlightbackground="#d9d9d9")
        self.Radiobutton1.configure(highlightcolor="black")
        self.Radiobutton1.configure(justify=LEFT)
        self.Radiobutton1.configure(text='''Playlists Saved in Pocket''')
        self.Radiobutton1.configure(value='Pocket')
        self.Radiobutton1.configure(variable=GUI_Support.choice)

        self.Radiobutton2 = Radiobutton(self.Labelframe4)
        self.Radiobutton2.place(relx=0.51, rely=0.2, relheight=0.18
                , relwidth=0.42)
        self.Radiobutton2.configure(activebackground="#d9d9d9")
        self.Radiobutton2.configure(activeforeground="#000000")
        self.Radiobutton2.configure(background="#444444")
        self.Radiobutton2.configure(disabledforeground="#a3a3a3")
        self.Radiobutton2.configure(foreground="#09bbf7")
        self.Radiobutton2.configure(highlightbackground="#d9d9d9")
        self.Radiobutton2.configure(highlightcolor="black")
        self.Radiobutton2.configure(justify=LEFT)
        self.Radiobutton2.configure(text='''From Playlist URL''')
        self.Radiobutton2.configure(value='URL')
        self.Radiobutton2.configure(width=223)
        self.Radiobutton2.configure(variable=GUI_Support.choice)

        self.Message1 = Message(self.Labelframe4)
        self.Message1.place(relx=0.06, rely=0.68, relheight=0.25, relwidth=0.4)
        self.Message1.configure(background="#444444")
        self.Message1.configure(font=font11)
        self.Message1.configure(foreground="#ffffff")
        self.Message1.configure(highlightbackground="#d9d9d9")
        self.Message1.configure(highlightcolor="black")
        self.Message1.configure(justify=CENTER)
        self.Message1.configure(text='''Multiple URLs can be used separated by ;''')
        self.Message1.configure(width=210)

        self.Labelframe5 = LabelFrame(top)
        self.Labelframe5.place(relx=0.05, rely=0.06, relheight=0.36
                , relwidth=0.88)
        self.Labelframe5.configure(relief=RIDGE)
        self.Labelframe5.configure(font=font11)
        self.Labelframe5.configure(foreground="#caf35c")
        self.Labelframe5.configure(relief=RIDGE)
        self.Labelframe5.configure(text='''Billboard Charts to Google Music''')
        self.Labelframe5.configure(background="#444444")
        self.Labelframe5.configure(highlightbackground="#d9d9d9")
        self.Labelframe5.configure(highlightcolor="black")
        self.Labelframe5.configure(width=530)

        self.Button6 = Button(self.Labelframe5)
        self.Button6.place(relx=0.68, rely=0.37, height=42, width=148)
        self.Button6.configure(activebackground="#d9d9d9")
        self.Button6.configure(activeforeground="#000000")
        self.Button6.configure(background="#caf35c")
        self.Button6.configure(disabledforeground="#a3a3a3")
        self.Button6.configure(foreground="#000000")
        self.Button6.configure(highlightbackground="#d9d9d9")
        self.Button6.configure(highlightcolor="black")
        self.Button6.configure(pady="0")
        self.Button6.configure(text='''Create Playlist''')
        self.Button6.configure(width=148)
        self.Button6.configure(command = self.billboard)

        self.Checkbutton1 = Checkbutton(self.Labelframe5)
        self.Checkbutton1.place(relx=0.09, rely=0.19, relheight=0.21
                , relwidth=0.35)
        self.Checkbutton1.configure(activebackground="#d9d9d9")
        self.Checkbutton1.configure(activeforeground="#000000")
        self.Checkbutton1.configure(anchor=W)
        self.Checkbutton1.configure(background="#444444")
        self.Checkbutton1.configure(disabledforeground="#a3a3a3")
        self.Checkbutton1.configure(font=font11)
        self.Checkbutton1.configure(foreground="#f39521")
        self.Checkbutton1.configure(highlightbackground="#d9d9d9")
        self.Checkbutton1.configure(highlightcolor="black")
        self.Checkbutton1.configure(justify=LEFT)
        self.Checkbutton1.configure(text='''Hot 100 and Risers''')
        self.Checkbutton1.configure(variable=GUI_Support.hot_100)

        self.Checkbutton2 = Checkbutton(self.Labelframe5)
        self.Checkbutton2.place(relx=0.09, rely=0.37, relheight=0.21
                , relwidth=0.39)
        self.Checkbutton2.configure(activebackground="#d9d9d9")
        self.Checkbutton2.configure(activeforeground="#000000")
        self.Checkbutton2.configure(anchor=W)
        self.Checkbutton2.configure(background="#444444")
        self.Checkbutton2.configure(disabledforeground="#a3a3a3")
        self.Checkbutton2.configure(font=font11)
        self.Checkbutton2.configure(foreground="#ff392f")
        self.Checkbutton2.configure(highlightbackground="#d9d9d9")
        self.Checkbutton2.configure(highlightcolor="black")
        self.Checkbutton2.configure(justify=LEFT)
        self.Checkbutton2.configure(text='''Top R&B & HipHop''')
        self.Checkbutton2.configure(variable=GUI_Support.hiphop)
        self.Checkbutton2.configure(width=208)

        self.Checkbutton3 = Checkbutton(self.Labelframe5)
        self.Checkbutton3.place(relx=0.09, rely=0.54, relheight=0.21
                , relwidth=0.35)
        self.Checkbutton3.configure(activebackground="#d9d9d9")
        self.Checkbutton3.configure(activeforeground="#000000")
        self.Checkbutton3.configure(anchor=W)
        self.Checkbutton3.configure(background="#444444")
        self.Checkbutton3.configure(disabledforeground="#a3a3a3")
        self.Checkbutton3.configure(font=font11)
        self.Checkbutton3.configure(foreground="#09bbf7")
        self.Checkbutton3.configure(highlightbackground="#d9d9d9")
        self.Checkbutton3.configure(highlightcolor="black")
        self.Checkbutton3.configure(justify=LEFT)
        self.Checkbutton3.configure(text='''Top EDM''')
        self.Checkbutton3.configure(variable=GUI_Support.edm)


    def spotify(self):
        # print "spotify"
        if GUI_Support.choice.get()=='Pocket':
            Spotify_to_GoogleMusic.scan_pocket()
        else:
            urls = GUI_Support.urls.get().split(';')
            for url in urls:
                Spotify_to_GoogleMusic.main(url,False)


    def billboard(self):
        # print "billboard"
        temp_list = []
        for key,display_name in Billboard_to_GoogleMusic.charts_to_playlist:
            if GUI_Support.hot_100.get() == 1 and key == 'HOT_100':
                temp_list.append((key,display_name))
            if GUI_Support.hiphop.get() == 1 and key == 'TOP_HIPHOP':
                temp_list.append((key,display_name))
            if GUI_Support.edm.get() == 1 and key == 'TOP_EDM':
                temp_list.append((key,display_name))
        Billboard_to_GoogleMusic.charts_to_playlist = temp_list

        Billboard_to_GoogleMusic.main()
        # print (GUI_Support.hot_100.get())




if __name__ == '__main__':
    vp_start_gui()


