#!/usr/bin/env python
import os
import time
from datetime import datetime
import subprocess
import json
from Tkinter import *
import tkFont

"""
*******************************************************************************
    TITLE:   What To Watch
	PURPOSE: Search folder and subfolders for unwatched videos,
        then display the results so the user can select which video(s) to watch
	AUTHOR:  Jimmy McCann
	USAGE: WhatToWatch
	REVISION HISTORY:
	    *JWM 07/2014 Created
	    *JWM 12/2015 Cleaned up formatting and adding documentation
*******************************************************************************
"""

from BusyManager import BusyManager
from Splash import Splash


"""
----------
    NAME:
    DESCRIPTION:
    KEYWORDS:
    CALLED BY: main
    EXTENDS:
    ASSUMES:
    SIDE EFFECTS:
"""
class WhatToWatch(Frame):

    """
    ----------
        NAME:
        DESCRIPTION:
        KEYWORDS:
        CALLED BY:
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS:
    """
    def __init__(self, parent, args):
        Frame.__init__(self, parent)

        self.parent = parent
        self.manager = BusyManager(self.parent)
        self.load_configuration()
        self.name_location = {}
        self.watch_me(args[0])  # SEARCHFOLDER = "\\\\RT-AC68U-1D30\\Libraries\\Videos"
        self.initUI()

    """
    ----------
        NAME:
        DESCRIPTION:
        KEYWORDS:
        CALLED BY:
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS:
    """
    def load_configuration(self):
        with open('config') as f:
            data = f.read()
        jsonDict = json.loads(data)
        self.VIDEOS = jsonDict['videoExts']
        self.SKIP = jsonDict['skipFiles']
        self.VIDPROGRAM = os.path.join(*jsonDict['videoProgramPath'])

    """
    ----------
        NAME:
        DESCRIPTION:
        KEYWORDS:
        CALLED BY:
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS:
    """
    def watch_me(self, folder):
        now = datetime.fromtimestamp(time.time())
        self.manager.busy()
        for root, folders, files in os.walk(folder):
            for fileName in files:
                name, extension = os.path.splitext(fileName)
                if extension.upper() in self.VIDEOS and not any(s in name.upper() for s in self.SKIP):
                    filepath = os.path.join(root, fileName)
                    stats = os.stat(filepath)
                    created = datetime.fromtimestamp(stats.st_ctime)
                    accessed = datetime.fromtimestamp(stats.st_atime)
                    if (accessed - created).days <= 1 or (now - accessed).days > 365:
                        self.name_location[name] = filepath
        self.manager.notbusy()

    """
    ----------
        NAME:
        DESCRIPTION:
        KEYWORDS:
        CALLED BY:
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS:
    """
    def init_ui(self):
        self.parent.title("Downloads to Watch")
        self.pack(fill=BOTH,
                  expand=1)

        largefont = tkFont.Font(size=18)

        self.LB = Listbox(self,
                          bd=1,
                          height=20,
                          font=largefont)
        maxwidth = 0
        for movie in self.name_location.keys():
            self.LB.insert(END, movie)
            if len(movie) > maxwidth:
                maxwidth = len(movie)
        self.LB.config(width=maxwidth)
        self.LB.pack(side=LEFT,
                     fill=BOTH,
                     expand=True)

        S = Scrollbar(self)
        S.pack(side=RIGHT,
               fill=Y,
               expand=1)
        S.config(command=self.LB.yview)
        
        self.LB.config(yscrollcommand=S.set)

        self.LB.bind("<Double-Button-1>",
                     self.on_double)

    """
    ----------
        NAME:
        DESCRIPTION:
        KEYWORDS:
        CALLED BY:
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS:
    """
    def on_double(self, event):
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])
        p = subprocess.call([self.VIDPROGRAM,
                             self.name_location[value]])
        self.LB.delete(selection)


"""
----------
    NAME:
    DESCRIPTION:
    KEYWORDS:
    CALLED BY:
    PARAMETERS:
    RETURNS:
    ASSUMES:
    SIDE EFFECTS:
"""
def main(args):
    root = Tk()
    with Splash(root, 'splashImage.gif', 10.0):
        WhatToWatch(root,
                    args)
    root.mainloop()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1:])
