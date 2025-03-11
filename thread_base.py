import threading
from logger import Logger

class ThreadBase(threading.Thread):

    def __init__(self, logname, api=None, shared=None, lock: threading.Lock=None, events=None):
        super().__init__()
        self.shared = shared
        self.lock = lock
        self.events = events
        self.api = api
        self.log = Logger(logname)

    def log_message(self, msg, error=False):
        if error == True:
            self.log.logger.error(msg)
        else:            
            self.log.logger.debug(msg)