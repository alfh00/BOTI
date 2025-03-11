from PositionProcessor import PositionProcessor
from apis.PriceStreamer import PriceStreamer
from apis.bitget_client import BitgetClient
from logger import Logger
from models.trade_settings import TradeSettings
from models.api_secrets import ApiSecrets
from PriceProcessor import PriceProcessor
from Strategy import Strategy
import json
import time
import threading
from queue import Queue

from OrderManager import OrderManager

import atexit

class TraderBot():
    ERROR_LOG = 'error'
    MAIN_LOG = 'main'
    GRANULARITY = '1m'
    ACCOUNT= 'bitget1'
    

    def __init__(self):
        # Load settings and secrets
        self.load_settings()
        self.load_secrets()
        self.setup_logs()

        
        self.shared_prices = {symbol: None for symbol in self.trade_settings.keys()}
        self.price_lock = threading.Lock() 
        self.price_events = {symbol: threading.Event() for symbol in self.trade_settings.keys()}
        self.shared_positions = {symbol: None for symbol in self.trade_settings.keys()}
        self.position_lock = threading.Lock() 
        self.position_events = {symbol: threading.Event() for symbol in self.trade_settings.keys()}
        
        self.price_queue = {symbol: Queue() for symbol in self.trade_settings.keys()}
        self.candle_queue = {symbol: Queue() for symbol in self.trade_settings.keys()}
        self.position_queue = {symbol: Queue() for symbol in self.trade_settings.keys()}

        # self.trade_queue = Queue()

        self.shutdown_event = threading.Event()
        

        threads = []


        # Initialize API client, PriceStreamer and DataManager
        self.api = BitgetClient(self.api_secrets.apiKey, self.api_secrets.secretKey, self.api_secrets.passphrase)

        self.price_streamer = PriceStreamer(self.shared_prices,
                                            self.price_lock, 
                                            self.price_events, 
                                            self.shared_positions, 
                                            self.position_lock, 
                                            self.position_events, 
                                            self.api_secrets.apiKey, 
                                            self.api_secrets.secretKey, 
                                            self.api_secrets.passphrase)
        
        

        for pair, pair_setting in self.trade_settings.items():
            price_processor_t = PriceProcessor(self.shared_prices, 
                                               self.price_lock, 
                                               self.price_events, 
                                               self.price_queue,
                                               self.candle_queue,                          
                                               f'PriceProcess_{pair}', 
                                               pair, 
                                               pair_setting.granularity,
                                               self.shutdown_event
                                               )
            price_processor_t.daemon = False
            threads.append(price_processor_t)
            price_processor_t.start()
        
        for pair, pair_setting in self.trade_settings.items():
            position_processor_t = PositionProcessor(self.shared_positions, 
                                                    self.position_lock, 
                                                    self.position_events, 
                                                    self.position_queue[pair],                         
                                                    f'PositionProcess_{pair}', 
                                                    pair, 
                                                    self.shutdown_event
                                                    )
            position_processor_t.daemon = False
            threads.append(position_processor_t)
            position_processor_t.start()
        
        for pair, pair_setting in self.trade_settings.items():
            strategy_processor_t = Strategy(self.price_queue[pair],
                                            self.candle_queue[pair],
                                            self.position_queue[pair],
                                            self.api,
                                            OrderManager,                      
                                            f'StrategyProcess_{pair}', 
                                            pair, 
                                            self.trade_settings[pair],
                                            self.shutdown_event
                                            )
            strategy_processor_t.daemon = False
            threads.append(strategy_processor_t)
            strategy_processor_t.start()

    def setup_logs(self):
        self.logs = {}
        for k in self.trade_settings.keys():
            self.logs[k] = Logger(k)
            self.log_message(f'{self.trade_settings[k]}', k)
        self.logs[TraderBot.ERROR_LOG] = Logger(TraderBot.ERROR_LOG)
        self.logs[TraderBot.MAIN_LOG] = Logger(TraderBot.MAIN_LOG)
        self.log_to_main(f'TraderBot started with {TradeSettings.settings_to_str(self.trade_settings)}')
    
        
    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, TraderBot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, TraderBot.ERROR_LOG)

    def load_settings(self):
        with open('./setting.json', 'r') as f:
            data = json.loads(f.read())
            self.trade_settings = {symbol: TradeSettings(settings) for symbol, settings in data.items()}
            # print(self.trade_settings)

    
    def load_secrets(self):
        with open('./secrets.json', 'r') as f:
            data = json.loads(f.read())
            data = data[self.ACCOUNT]
            self.api_secrets = ApiSecrets(data) 


    def run(self):
        pass

    def shutdown(self):
        print("Shutting down all threads...")
        self.shutdown_event.set()  # Signal all threads to stop

        # Clear queues or perform other cleanup here
        # Cancel all orders

        # Wait for all threads to finish
        for thread in threading.enumerate():
            if thread != threading.current_thread():
                thread.join()

        print("All threads have been shut down gracefully.")





if __name__ == '__main__':
    b = TraderBot()
    atexit.register(b.shutdown)  # Register shutdown method to be called on exit

    try:
        # Your main program logic here
        while True:
            pass  # Replace with your main loop
    except KeyboardInterrupt:
        print("Received keyboard interrupt, shutting down...")
        b.shutdown()
