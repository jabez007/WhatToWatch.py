#!/usr/bin/env python
__author__ = 'Jimmy'
#http://www.groovypost.com/howto/microsoft/enable-last-access-time-stamp-to-files-folder-windows-7/
import sys #http://www.diveintopython.net/scripts_and_streams/command_line_arguments.html
import os,time
from datetime import datetime
import subprocess
import json
from Tkinter import *
from BusyManager import BusyManager
from Splash import Splash
from dateutil.relativedelta import relativedelta

#VIDEOS = ['.AVI','.FLV','.M4V','.MKV','.MP4','.MPG','.WTV']
#SKIP = ['SAMPLE','ETRG','RARBG.COM','EXTRATORRENTRG']
#VIDPROGRAM = "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"

class WhatToWatch(Frame):
    def __init__(self, parent, args):
        Frame.__init__(self, parent)

        self.parent = parent
        self.manager = BusyManager(self.parent)
        self.load_configuration()
        self.name_location = {}
        self.watch_me(args[0]) #SEARCHFOLDER = "\\\\RT-AC68U-1D30\\Libraries\\Videos"
        self.initUI()

    def load_configuration(self):
        with open('config') as f:
            data = f.read()
        jsonDict = json.loads(data)
        self.VIDEOS = jsonDict['videoExts']
        self.SKIP = jsonDict['skipFiles']
        self.VIDPROGRAM = os.path.join(*jsonDict['videoProgramPath'])

    def watch_me(self, folder):
        NOW = datetime.fromtimestamp(time.time())
        self.manager.busy()
        for root,folders,files in os.walk(folder):
            for fileName in files:
                #print ".",
                name,extension = os.path.splitext(fileName)
                if extension.upper() in self.VIDEOS and not any(s in name.upper() for s in self.SKIP):
                    filePath = os.path.join(root,fileName)
                    stats = os.stat(filePath)
                    created = datetime.fromtimestamp(stats.st_ctime)
                    accessed = datetime.fromtimestamp(stats.st_atime)
                    if relativedelta(accessed,created).days < 1 or relativedelta(NOW,accessed).years > 1:
                        self.name_location[name] = filePath
        self.manager.notbusy()

    def initUI(self):
        self.parent.title("Downloads to Watch")

        self.pack(fill=BOTH, expand=1)

        self.LB = Listbox(self, height=20, width=100)
        for movie in self.name_location.keys():
            self.LB.insert(END, movie)

        self.LB.pack(side=LEFT, fill=BOTH)

        S = Scrollbar(self)
        S.pack(side=RIGHT, fill=Y)
        S.config(command=self.LB.yview)
        self.LB.config(yscrollcommand=S.set)

        self.LB.bind("<Double-Button-1>", self.on_double)

    def on_double(self, event):
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])
        #print "Selection:",selection,": '%s'" % value
        p = subprocess.call([self.VIDPROGRAM,self.name_location[value]])
        self.LB.delete(selection)


def main(args):
    root = Tk()
    with Splash(root, 'splashImage.gif', 10.0):
        WhatToWatch(root,args)
    root.mainloop()

if __name__=='__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1:])