import logging
import os

LOG_FORMAT = '%(asctime)s %(message)s'
DEFAULT_LEVEL = logging.DEBUG

class Logger:

    PATH= './logs'

    def __init__(self, name, mode='w'):
        self.create_dir()
        self.filename = f'{Logger.PATH}/{name}.log'
        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEFAULT_LEVEL)

        file_handler = logging.FileHandler(self.filename, mode=mode)
        formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f'Logger init() {self.filename}')


    def create_dir(self):

        if not os.path.exists(Logger.PATH):
            os.mkdir(Logger.PATH)
    
