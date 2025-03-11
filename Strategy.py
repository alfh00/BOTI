import pandas as pd
from thread_base import ThreadBase
from apis.bitget_client import BitgetClient
from OrderManager import OrderManager

from models.live_position import LivePosition
from models.live_prices import LiveStreamPrice
from models.trade_settings import TradeSettings

class Strategy(ThreadBase):

    def __init__(self, price_queue, candle_queue, position_queue, api, order_manager, logname, pair, settings, shutdown_event):
        super().__init__(logname=logname, api=api)
        self.pair = pair
        self.settings : TradeSettings = settings
        self.api: BitgetClient = api
        self.df = None
        self.candle_queue= candle_queue
        self.price_queue= price_queue
        self.position_queue= position_queue
        self.order_manager: OrderManager = order_manager(self.pair, self.api, settings.risk)
        self.long_position = None
        self.short_position = None
        self.shutdown_event = shutdown_event

    def update_df(self, candle):
        if self.df is None:
            params = {
            "symbol": self.pair,  
            "productType": "USDT-FUTURES",  
            "granularity": self.settings.granularity,  
            "limit": "100"
            }
            ohlc_data = self.api.candles(params)['data']
            df = pd.DataFrame(ohlc_data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume', 'QuoteAssetVolume']).astype(float)

            # Convert the Timestamp column to datetime
            df['datetime'] = pd.to_numeric(df['datetime'])
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

            # Set the Timestamp column as the index
            df.set_index('datetime', inplace=True)
            self.df = df
            
        else:
            new_row = pd.DataFrame([candle]).set_index('datetime')
            temp_df = pd.concat([self.df, new_row], ignore_index=False)
            self.df = temp_df[-100:]

        
    
    # def get_orders(self):
    #     return self.api.get_open_position(symbol=self.pair)
    
    def run_analysis(self):
        pass

    # def process_bid_ask(self, price):
    #     try:
    #         self.price_lock.acquire()
    #         # price = copy.deepcopy(self.shared_prices[self.pair])
    #         print(f'Strategy bid: {price.bid}, ask: {price.ask}')
            
    #         # Further processing based on bid and ask prices
    #     except Exception as e:
    #         self.log_message(f'CRASH : {e}', error=True)
    #     finally:
    #         self.price_lock.release()
    def _find_high_low(self, candle, df, window=5):
    
        PIVOT_H = 1
        PIVOT_L = -1
        
        if ((candle-window) <0) | ((candle+window)>=len(df)):
            return 0
        
        pivot_high = True
        pivot_low = True
        
        for i in range(candle - window, candle + window + 1):
            if df.iloc[candle].high < df.iloc[i].high:
                pivot_high = False
            if df.iloc[candle].low > df.iloc[i].low:
                pivot_low = False
        
        if pivot_high and pivot_low:
            return 0
        elif pivot_high:
            return PIVOT_H
        elif pivot_low:
            return PIVOT_L
        else:
            return 0 
        
    def populate_indicators(self):
        
        df = self.df
        df = df.reset_index()
        df['hh_ll'] = df.apply(lambda row: self._find_high_low(row.name, df), axis=1)
        df.set_index('datetime', inplace=True)

        self.df = df 

    def find_last_h_l(self):
        df = self.df

        last_h_l = {"hh": None, "ll": None}

        for index, row in df.iterrows():
            # Update the last higher-high (HH) and lower-low (LL) if there's a pivot high or low
            if row['hh_ll'] == 1:  # New pivot high
                last_h_l['hh'] = row['high']
            elif row['hh_ll'] == -1:  # New pivot low
                last_h_l['ll'] = row['low']

            # Store the last HH and LL in the data frame
            df.loc[index, 'hh'] = last_h_l['hh']
            df.loc[index, 'll'] = last_h_l['ll']

        self.df = df   

    def peek(self):
        try:
            return self.candle_queue[0]
        except IndexError:
            return None
    
    def check_position(self, position: LivePosition):
        if position is not None:
            if position.is_long():
                if position.is_active():
                    self.long_position = position
                else:
                    self.long_position = None
            else:
                if position.is_active():
                    self.short_position = position
                else:
                    self.short_position = None
        
    def place_trigger_orders(self):
        if self.long_position is None:
            hh = self.df['hh'].iloc[-1]
            # print(hh)
            long_order_price = hh #- (hh * self.settings.dist)
            sl = long_order_price - (long_order_price * self.settings.sl_pct)
            tp = long_order_price + (long_order_price * self.settings.tp_pct)
            print(self.order_manager.place_trigger_order('buy', 'limit', long_order_price, sl, tp))

        if self.short_position is None:
            ll = self.df['ll'].iloc[-1]
            # print(ll)
            short_order_price = ll #+ (ll * self.settings.dist)
            sl = short_order_price + (short_order_price * self.settings.sl_pct)
            tp = short_order_price - (short_order_price * self.settings.tp_pct)
            print(self.order_manager.place_trigger_order('sell', 'limit', short_order_price, sl, tp))

    def pick_upcoming_price(self):
        if not self.price_queue.empty():
            new_price = self.price_queue.get()
            print(new_price)
            # trail stop

    def pick_upcoming_position(self):
        if not self.position_queue.empty():
            position = self.position_queue.get()
            print('UPCOMING POSITION', position)
            # check opening closing position 
            # return self.check_position(position)
    
    def pick_upcoming_candle(self):
        if not self.candle_queue.empty():
            candle = self.candle_queue.get()
            # print(candle) # print for debug
            self.update_df(candle)
            self.populate_indicators()
            self.find_last_h_l()
            self.log_message(f'DF updated :\n {self.df.tail(2)}')
            self.place_trigger_orders()

    
    def run(self):
        while not self.shutdown_event.is_set():
            # --- On new price
            self.pick_upcoming_price()
            # --- On new position
            self.pick_upcoming_position()
            # --- On new candle
            self.pick_upcoming_candle()
        
        print(f"{self.name} is shutting down gracefully.")
            

                    
        