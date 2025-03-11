import datetime
import pytz
import requests
import pandas as pd
import json

from typing import List, Tuple


# f = open(
#     "./secret.json",
# )
# secret = json.load(f)
# f.close()

# api_key = "your-api-key"
# api_secret = "your-secret-key"
# api_passphrase = "your-api-passphrase"

class BitgetClient:
    BASE_URL = 'https://api.bitget.com/api/v2'
    MARK_PRICE_URL = 'https://api.bitget.com/api/v2/mix/market/candles'
    GRANULARITY = '5m'
    PRODUCT: str ='USDT-FUTURES'

    def _get_last_candles(self,  symbol, n):

        data = []
    
        for start_time, end_time in self._generate_intervals(n):

            start_time = int(start_time.timestamp()) * 1000
            end_time = int(end_time.timestamp()) * 1000

            params = {
                            "symbol": f"{symbol}",
                            "productType": self.PRODUCT,
                            "granularity": self.GRANULARITY,
                            "limit": "1000",
                            "KLineType": 'MARKET tick',
                            "startTime": start_time,
                            "endTime": end_time
                        }


            response = requests.get(self.MARK_PRICE_URL, params=params)
            temp_candles = response.json()['data']
            data.extend(temp_candles)
        return data

    

    def _generate_intervals(self, n):
        intervals = []
        now = datetime.datetime.now() 
        start_datetime = now - datetime.timedelta(minutes=n*5)
        
        range = 1000
        # Define the size of the intervals for each timeframe
        timeframe_intervals = {
            '1W': datetime.timedelta(weeks=1*12),
            '1m': datetime.timedelta(minutes=1*range),
            '5m': datetime.timedelta(minutes=5*range),
            '15m': datetime.timedelta(minutes=15*range),
            '30m': datetime.timedelta(minutes=30*range),
            '1H': datetime.timedelta(hours=1*range),
            '4H': datetime.timedelta(hours=4*range),
            '1D': datetime.timedelta(days=1*90),
        }

        # Get the size of the intervals for the specified timeframe
        interval = timeframe_intervals[self.GRANULARITY]

        # Generate the intervals
        while start_datetime < now:
            next_datetime = start_datetime + interval
            if next_datetime > now:
                next_datetime = now
            intervals.append((start_datetime.replace(second=0, microsecond=0), next_datetime.replace(second=0, microsecond=0)))
            start_datetime = next_datetime

        return intervals
    
    def get_last_candles_df(self, symbol, n=200):
        df = pd.DataFrame(self._get_last_candles(symbol, n), columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'quoteVolume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms', origin='unix')
        df.set_index('timestamp', inplace=True)
        return df

    def place_trigger_order(self, symbol, product_type, margin_mode, margin_coin, size, trigger_price, price=None,
                        stop_surplus_trigger_price=None, stop_loss_trigger_price=None,
                        side='buy', trade_side='open', order_type='limit', trigger_type='mark_price'):
        """
        Places a trigger order with optional take-profit and stop-loss settings.

        Args:
            symbol (str): Trading pair, e.g., 'BTCUSDT'.
            product_type (str): Product type, e.g., 'usdt-futures'.
            margin_mode (str): Margin mode, either 'isolated' or 'cross'.
            margin_coin (str): Margin coin, e.g., 'USDT'.
            size (str): Order size, e.g., '0.01'.
            trigger_price (str): Price at which the order will be triggered.
            price (str, optional): Strike price if orderType is 'limit'.
            stop_surplus_trigger_price (str, optional): Take-profit trigger price.
            stop_loss_trigger_price (str, optional): Stop-loss trigger price.
            side (str): Order direction ('buy' or 'sell').
            trade_side (str): Trade side ('open' or 'close').
            order_type (str): Order type ('limit' or 'market').
            trigger_type (str): Trigger type ('mark_price', 'fill_price', or 'index_price').

        Returns:
            dict: Response from the API with order ID and status.
        """

        url = f"{self.BASE_URL}/api/v2/mix/order/place-plan-order"

        # Create payload for the trigger order
        payload = {
            "planType": "normal_plan",
            "symbol": symbol,
            "productType": product_type,
            "marginMode": margin_mode,
            "marginCoin": margin_coin,
            "size": size,
            "price": price,
            "triggerPrice": trigger_price,
            "triggerType": trigger_type,
            "side": side,
            "tradeSide": trade_side,
            "orderType": order_type,
            "presetStopSurplusPrice": stop_surplus_trigger_price,
            "stopSurplusTriggerPrice": stop_surplus_trigger_price,
            "presetStopLossPrice": stop_loss_trigger_price,
            "stopLossTriggerPrice": stop_loss_trigger_price
        }

        # Convert payload to JSON format
        payload_json = json.dumps(payload)

        # Get headers
        headers = get_headers(API_KEY, API_SECRET, API_PASSPHRASE, payload_json, 'POST', '/api/v2/mix/order/place-plan-order')

        # Send POST request to Bitget API
        response = requests.post(url, headers=headers, data=payload_json)

        return response.json()
    def get_account_balance(self):
        pass

# # Example Usage
# response = place_trigger_order(
#     symbol="BTCUSDT",
#     product_type="usdt-futures",
#     margin_mode="isolated",
#     margin_coin="USDT",
#     size="0.01",
#     trigger_price="24100",
#     price="24000",  # Omit this if placing a market order
#     stop_surplus_trigger_price="24500",
#     stop_loss_trigger_price="23000",
#     side="buy",
#     trade_side="open",
#     order_type="limit",  # 'limit' or 'market'
#     trigger_type="mark_price"
# )

import time
import hmac
import hashlib
import requests
import json

class BitgetClient:
    def __init__(self, api_key, secret_key, passphrase, base_url="https://api.bitget.com"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = base_url
        self.session = requests.Session()

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, method, path, body):
        """Create HMAC SHA256 signature for Bitget API."""
        timestamp = self._get_timestamp()
        message = timestamp + method.upper() + path + (json.dumps(body) if body else "")
        hmac_key = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac_key, timestamp

    def _create_headers(self, method, path, body=None):
        """Create headers including the signature."""
        signature, timestamp = self._sign(method, path, body)
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": self.passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US"
        }

    def _send_request(self, method, path, body=None):
        """Send HTTP request using the session."""
        url = self.base_url + path
        headers = self._create_headers(method, path, body)
        
        if method == "GET":
            response = self.session.get(url, headers=headers, params=body)
        elif method == "POST":
            response = self.session.post(url, headers=headers, data=json.dumps(body))
        
        # Handle response and errors
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    # Example API function to place a trigger order
    def place_trigger_order(self, symbol, product_type, margin_mode, margin_coin, size, price, trigger_price, trigger_type, side, trade_side, order_type):
        """Place a trigger order using the Bitget API."""
        path = "/api/v2/mix/order/place-plan-order"
        body = {
            "planType": "normal_plan", 
            "symbol": symbol,
            "productType": product_type,
            "marginMode": margin_mode,
            "marginCoin": margin_coin,
            "size": size,
            "price": price,
            "triggerPrice": trigger_price,
            "triggerType": trigger_type,
            "side": side,
            "tradeSide": trade_side,
            "orderType": order_type
        }
        return self._send_request("POST", path, body)

# Example usage
if __name__ == "__main__":
    api_key = "your_api_key"
    secret_key = "your_secret_key"
    passphrase = "your_passphrase"
    
    client = BitgetClient(api_key, secret_key, passphrase)
    
    # Example of placing a trigger order
    try:
        result = client.place_trigger_order(
            symbol="BTCUSDT",
            product_type="usdt-futures",
            margin_mode="isolated",
            margin_coin="USDT",
            size="0.01",
            price="24000",
            trigger_price="24100",
            trigger_type="mark_price",
            side="buy",
            trade_side="open",
            order_type="limit"
        )
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")

import ccxt
import pandas as pd
import time
from multiprocessing.pool import ThreadPool as Pool
import numpy as np

class PerpBitget():
    def __init__(self, apiKey=None, secret=None, password=None):
        bitget_auth_object = {
            "apiKey": apiKey,
            "secret": secret,
            "password": password,
            'options': {
            'defaultType': 'swap',
        }
        }
        if bitget_auth_object['secret'] == None:
            self._auth = False
            self._session = ccxt.bitget()
        else:
            self._auth = True
            self._session = ccxt.bitget(bitget_auth_object)
        self.market = self._session.load_markets()

    def authentication_required(fn):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not self._auth:
                # print("You must be authenticated to use this method", fn)
                raise Exception("You must be authenticated to use this method")
            else:
                return fn(self, *args, **kwargs)
        return wrapped

    def get_last_historical(self, symbol, timeframe, limit):
        result = pd.DataFrame(data=self._session.fetch_ohlcv(
            symbol, timeframe, None, limit=limit))
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result

    def get_more_last_historical_async(self, symbol, timeframe, limit):
        max_threads = 4
        pool_size = round(limit/100)  # your "parallelness"

        # define worker function before a Pool is instantiated
        full_result = []
        def worker(i):
            
            try:
                return self._session.fetch_ohlcv(
                symbol, timeframe, round(time.time() * 1000) - (i*1000*60*60), limit=100)
            except Exception as err:
                raise Exception("Error on last historical on " + symbol + ": " + str(err))

        pool = Pool(max_threads)

        full_result = pool.map(worker,range(limit, 0, -100))
        full_result = np.array(full_result).reshape(-1,6)
        result = pd.DataFrame(data=full_result)
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result.sort_index()

    def get_bid_ask_price(self, symbol):
        try:
            ticker = self._session.fetchTicker(symbol)
        except BaseException as err:
            raise Exception(err)
        return {"bid":ticker["bid"],"ask":ticker["ask"]}

    def get_min_order_amount(self, symbol):
        return self._session.markets_by_id[symbol]["info"]["minProvideSize"]

    def convert_amount_to_precision(self, symbol, amount):
        return self._session.amount_to_precision(symbol, amount)

    def convert_price_to_precision(self, symbol, price):
        return self._session.price_to_precision(symbol, price)

    @authentication_required
    def place_limit_order(self, symbol, side, amount, price, reduce=False):
        try:
            return self._session.createOrder(
                symbol, 
                'limit', 
                side, 
                self.convert_amount_to_precision(symbol, amount), 
                self.convert_price_to_precision(symbol, price),
                params={"reduceOnly": reduce}
            )
        except BaseException as err:
            raise Exception(err)

    @authentication_required
    def place_limit_stop_loss(self, symbol, side, amount, trigger_price, price, reduce=False):
        
        try:
            return self._session.createOrder(
                symbol, 
                'limit', 
                side, 
                self.convert_amount_to_precision(symbol, amount), 
                self.convert_price_to_precision(symbol, price),
                params = {
                    'stopPrice': self.convert_price_to_precision(symbol, trigger_price),  # your stop price
                    "triggerType": "market_price",
                    "reduceOnly": reduce
                }
            )
        except BaseException as err:
            raise Exception(err)

    @authentication_required
    def place_market_order(self, symbol, side, amount, reduce=False):
        try:
            return self._session.createOrder(
                symbol, 
                'market', 
                side, 
                self.convert_amount_to_precision(symbol, amount),
                None,
                params={"reduceOnly": reduce}
            )
        except BaseException as err:
            raise Exception(err)

    @authentication_required
    def place_market_stop_loss(self, symbol, side, amount, trigger_price, reduce=False):
        
        try:
            return self._session.createOrder(
                symbol, 
                'market', 
                side, 
                self.convert_amount_to_precision(symbol, amount), 
                self.convert_price_to_precision(symbol, trigger_price),
                params = {
                    'stopPrice': self.convert_price_to_precision(symbol, trigger_price),  # your stop price
                    "triggerType": "market_price",
                    "reduceOnly": reduce
                }
            )
        except BaseException as err:
            raise Exception(err)

    @authentication_required
    def get_balance_of_one_coin(self, coin):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            raise Exception("An error occured", err)
        try:
            return allBalance['total'][coin]
        except:
            return 0

    @authentication_required
    def get_all_balance(self):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            raise Exception("An error occured", err)
        try:
            return allBalance
        except:
            return 0

    @authentication_required
    def get_usdt_equity(self):
        try:
            usdt_equity = self._session.fetchBalance()["info"][0]["usdtEquity"]
        except BaseException as err:
            raise Exception("An error occured", err)
        try:
            return usdt_equity
        except:
            return 0

    @authentication_required
    def get_open_order(self, symbol, conditionnal=False):
        try:
            return self._session.fetchOpenOrders(symbol, params={'stop': conditionnal})
        except BaseException as err:
            raise Exception("An error occured", err)

    @authentication_required
    def get_my_orders(self, symbol):
        try:
            return self._session.fetch_orders(symbol)
        except BaseException as err:
            raise Exception("An error occured", err)

    @authentication_required
    def get_open_position(self,symbol=None):
        try:
            positions = self._session.fetchPositions(params = {
                    "productType": "umcbl",
                })
            truePositions = []
            for position in positions:
                if float(position['contracts']) > 0 and (symbol is None or position['symbol'] == symbol):
                    truePositions.append(position)
            return truePositions
        except BaseException as err:
            raise Exception("An error occured in get_open_position", err)

    @authentication_required
    def cancel_order_by_id(self, id, symbol, conditionnal=False):
        try:
            if conditionnal:
                return self._session.cancel_order(id, symbol, params={'stop': True, "planType": "normal_plan"})
            else:
                return self._session.cancel_order(id, symbol)
        except BaseException as err:
            raise Exception("An error occured in cancel_order_by_id", err)
        
    @authentication_required
    def cancel_all_open_order(self):
        try:
            return self._session.cancel_all_orders(
                params = {
                    "marginCoin": "USDT",
                }
            )
        except BaseException as err:
            raise Exception("An error occured in cancel_all_open_order", err)
        
    @authentication_required
    def cancel_order_ids(self, ids=[], symbol=None):
        try:
            return self._session.cancel_orders(
                ids=ids,
                symbol=symbol,
                params = {
                    "marginCoin": "USDT",
                }
            )
        except BaseException as err:
            raise Exception("An error occured in cancel_order_ids", err)