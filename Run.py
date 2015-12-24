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
    NAME: WhatToWatch
    DESCRIPTION: User Interface for selecting which video to watch
    KEYWORDS:
    CALLED BY: main
    EXTENDS: Tkinter.Frame
    ASSUMES:
    SIDE EFFECTS:
"""
class WhatToWatch(Frame):

    """
    ----------
        NAME: __init__
        DESCRIPTION: initializer for WhatToWatch object
        KEYWORDS: init
        CALLED BY: WhatToWatch
        PARAMETERS:
                parent:
                args:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS: sets instance attributes
    """
    def __init__(self, parent, args):
        Frame.__init__(self, parent)

        self.parent = parent
        self.manager = BusyManager(self.parent)
        self.load_configuration()
        self.name_location = {}
        self.watch_me(args[0])  # SEARCHFOLDER = "\\\\RT-AC68U-1D30\\Libraries\\Videos"
        self.init_ui()

    """
    ----------
        NAME: load_configuration
        DESCRIPTION: Loads configuration from config file
        KEYWORDS: configuration
        CALLED BY: __init__
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS: sets instance attributes from config file
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
        NAME: watch_me
        DESCRIPTION: searches folder defined in args for unwatched (based on creation and last access time)
            videos (based on videoExts defined in config file)
        KEYWORDS: search
        CALLED BY: __init__
        PARAMETERS:
            folder: folder to search through, defined in args passed in
        RETURNS:
        ASSUMES:
        SIDE EFFECTS: sets instance attribute, dict(filename: filepath)
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
        NAME: init_ui
        DESCRIPTION: builds the GUI where a user can select which video to watch
        KEYWORDS: Initialize, User Interface
        CALLED BY: WhatToWatch
        PARAMETERS:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS: Builds graphical components for user interface
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
        NAME: on_double
        DESCRIPTION: Opens selected video with program defined in config file
        KEYWORDS: open
        CALLED BY: self.LB
        PARAMETERS:
            event:
        RETURNS:
        ASSUMES:
        SIDE EFFECTS: Plays video
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
    NAME: main
    DESCRIPTION: Fires off splash page while WhatToWatch searches for unwatch videos
    KEYWORDS: main, splash
    CALLED BY: user
    PARAMETERS:
        args: folder to search, input by user
    RETURNS:
    ASSUMES:
    SIDE EFFECTS: Starts GUI
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
