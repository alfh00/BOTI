import pandas as pd
from thread_base import ThreadBase
from models.live_prices import LiveStreamPrice
import threading
import datetime as dt
import pytz
import copy

GRANULARITIES = {
    '1m': 1,
    '5m': 5,
    '15m': 15,
    '1h': 60
}


class PriceProcessor(ThreadBase):
    def __init__(self, shared_prices, price_lock: threading.Lock, price_events, price_queue, candle_queue, logname, pair, granularity, shutdown_event):
        super().__init__(logname=logname, shared=shared_prices, lock=price_lock, events=price_events)
        self.pair = pair
        self.granularity = GRANULARITIES[granularity]
        self.current_candle_data_df = pd.DataFrame(columns=['time', 'price'])
        self.candle_queue= candle_queue
        self.price_queue= price_queue
        self.shutdown_event = shutdown_event
    
        now = dt.datetime.now(pytz.timezone('UTC'))
        self.set_last_candle(now)
        print(f'PriceProcessor {self.last_complete_candle_time} now: {now}')

    def set_last_candle(self, price_time:dt.datetime):
        self.last_complete_candle_time = self.round_time_down(
            price_time #- dt.timedelta(minutes=self.granularity)
        )

    def round_time_down(self, round_me: dt.datetime):
        reminder = round_me.minute % self.granularity
        candle_time = dt.datetime(round_me.year,
                                  round_me.month,
                                  round_me.day,
                                  round_me.hour,
                                  round_me.minute - reminder,
                                  tzinfo=pytz.timezone('UTC'))
        return candle_time

    def detect_new_candle(self, price: LiveStreamPrice):
        old = self.last_complete_candle_time
        self.set_last_candle(price.time)
        if old < self.last_complete_candle_time:
            candle = self.construct_candle()
            self.update_candle(self.pair, candle)
            
            print(f'New Candle : {self.pair} Last Complete Candle {self.last_complete_candle_time} Current candle time {price.time}')

    def update_candle(self, symbol, candle):
        self.candle_queue[symbol].put(candle)

    def update_price(self, symbol, price):
        self.price_queue[symbol].put(price)

    def construct_candle(self):
        if not self.current_candle_data_df.empty:
            # Calculate the open, high, low, and close prices
            open_price = self.current_candle_data_df.iloc[0]['price']
            high_price = self.current_candle_data_df['price'].max()
            low_price = self.current_candle_data_df['price'].min()
            close_price = self.current_candle_data_df.iloc[-1]['price']
            
            # Create a dictionary with OHLC values and the timestamp of the candle
            candle_data = {
                'datetime': self.last_complete_candle_time,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': self.current_candle_data_df['volume'].sum() if 'volume' in self.current_candle_data_df.columns else 0,  # Add volume if available
            }
            
            # Print or log the constructed candle for debugging
            print(f"Constructed Candle: {candle_data}")
            
            # Reset the DataFrame for the next candle
            self.current_candle_data_df = pd.DataFrame(columns=['datetime', 'price'])
            
            return candle_data
        else:
            print("No data available to construct a candle.")
            return None

    def process_price(self):
        try:
            self.lock.acquire()
            price = copy.deepcopy(self.shared[self.pair])
            if price is not None:
                # todo : might update only if price changes ------------------
                self.update_price(self.pair, price)

                new_data = pd.DataFrame([{'time': price.time, 'price': price.price}])
                
                # Concatenate only if current_candle_data_df has data
                if not self.current_candle_data_df.empty:
                    self.current_candle_data_df = pd.concat([self.current_candle_data_df, new_data]).reset_index(drop=True)
                else:
                    # If empty, directly assign the new data to avoid concatenating with an empty DataFrame
                    self.current_candle_data_df = new_data
                
                # Print updated DataFrame
                # print('Current DataFrame:\n', self.current_candle_data_df)
                self.detect_new_candle(price)

        except Exception as e:
            self.log_message(f'CRASH : {e}', error=True)
        finally:
            self.lock.release()

    def run(self):
        while not self.shutdown_event.is_set():
            self.events[self.pair].wait()
            self.process_price()
            self.events[self.pair].clear()
        print(f"{self.name} is shutting down gracefully.")

