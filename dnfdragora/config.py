'''
dnfdragora is a graphical package management tool based on libyui python bindings

License: GPLv3

Author:  Angelo Naselli <anaselli@linux.it>

@package dnfdragora
'''

import sys
import yaml

from os.path import expanduser, join
import os


## TODO move to python-manatools
class AppConfig() :
    ''' AppConfig is an application configuration file management
    appName is the application name
    configuration file name is appName + ".yaml"
    which is searched in these places and order:
    1. from environment variable $'AppNme'
    2. current directory
    3. /etc/'AppName'/
    Application user preferences are loaded and saved into
    ~/.config/'appName'.yaml
    '''
    def __init__(self, appName):
        self._systemSettings = None
        self._userPrefs = None
        self.project    = appName
        self.variable = f"{appName.upper()}_CONF"
        self._fileName = f"{appName}.yaml"
        self.systemDir = f"/etc/{appName}"
        pathdir = os.path.expanduser("~") + "/.config/"
        self._userPrfesPathName  = os.path.join(pathdir, self._fileName)

    def _load(self):
        '''
        load system settings and user preferences
        '''
        if self._systemSettings is not None or self._userPrefs is not None:
            return
        self._userPrefs = {}
        pathdir = []
        if os.environ.get(self.variable) :
            pathdir.append(os.environ.get(self.variable))
        pathdir.extend([os.curdir, self.systemDir])

        print ("Try reading configuration file");
        for loc in pathdir:
            try:
                f = os.path.join(loc, self._fileName)
                print(f"From {f}")
                with open(f, 'r') as ymlfile:
                    self._systemSettings = yaml.safe_load(ymlfile)
                    break
            except IOError as e:
                print(f"Skipped exception: <{str(e)}> ")
        try:
            print(f"Finally read user settings from {self._userPrfesPathName}")
            with open(self._userPrfesPathName, 'r') as ymlfile:
                self._userPrefs = yaml.safe_load(ymlfile)
            if not self._userPrefs:
              self._userPrefs = {}
        except IOError as e:
            print(f"Skipped exception: <{str(e)}> ")

    @property
    def systemSettings(self) :
        '''
        returns system settings
        '''
        self._load()
        return self._systemSettings

    @property
    def userPreferences(self) :
        '''
        return user preferences
        '''
        self._load()
        return self._userPrefs


    def saveUserPreferences(self) :
        '''
        write user preferences into the related configuration file
        '''
        with open(self._userPrfesPathName, 'w') as outfile:
            yaml.dump(self._userPrefs, outfile, default_flow_style=False)

