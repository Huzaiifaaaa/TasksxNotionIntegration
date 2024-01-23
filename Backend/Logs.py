import os
import time
import logging
from logging.handlers import TimedRotatingFileHandler

from config import backend

class logs:
    def __init__(self,path):
        self.backend=backend()
        self.initializeDirectory(path)

        self.errorLogs = logging.getLogger('errorLogs')  
        self.errorLogs.setLevel(logging.ERROR)
        self.errorLogsHandler = TimedRotatingFileHandler(self.getFilePath(logging.ERROR,path), when='midnight', backupCount=5)
        self.errorFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.errorLogsHandler.setFormatter(self.errorFormat)
        self.errorLogs.addHandler(self.errorLogsHandler)

        self.infoLogs = logging.getLogger('infoLogs')  
        self.infoLogs.setLevel(logging.INFO)
        self.infoLogsHandler = TimedRotatingFileHandler(self.getFilePath(logging.INFO,path), when='midnight', backupCount=5)
        self.infoFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.infoLogsHandler.setFormatter(self.infoFormat)
        self.infoLogs.addHandler(self.infoLogsHandler)

    def initializeDirectory(self,path):
        os.makedirs(path+"error", exist_ok=True)
        os.makedirs(path+"info", exist_ok=True)


    def getFilePath(self,level,path):
        filepath=path+"error/"+str(time.strftime("%Y%m%d"))+".log"
        if logging.ERROR==level:
            filepath= path+"error/"+str(time.strftime("%Y%m%d"))+".log"
        elif logging.INFO==level:
            filepath=  path+"info/"+str(time.strftime("%Y%m%d"))+".log"

        return filepath



