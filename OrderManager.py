from datetime import datetime as dt
from apis.bitget_client import BitgetClient

class OrderManager:
    def __init__(self, symbol, api: BitgetClient, risk):
        """
        Initialize the OrderManager with an API session.
        :param api: An API Client session object that holds market information and provides order execution.
        """
        self.api = api
        self.symbol = symbol
        self.risk = risk

        self.contract = self.get_instrument_contract()
        if self.contract is None or not self.contract:
            raise ValueError(f"Could not retrieve contract details for {self.symbol}. Check symbol and product type.")
        self.volume_place = int(self.contract['volumePlace'])  # Get size precision
        self.price_place = int(self.contract['pricePlace'])    # Get price precision
        self.min_trade_num = float(self.contract['minTradeNum']) # Minimum trade amount

        self.order_tracker = {}  # Dictionary to track order status

        
        

    def oid(self):
        # Implement your order ID generation logic here.  A UUID is a good approach.
        import uuid
        return str(uuid.uuid4())
    
    def get_account_balance(self):
        try:
            response = self.api.account(dict(symbol=self.symbol, productType='USDT-FUTURES', marginCoin='USDT'))
            if response and 'data' in response:
                print(f"Account balance: {response['data']['available']}")
                return float(response['data']['available'])
            
            else:
                print(f"Unexpected response format: {response}")
                return None
        except Exception as e:
            print(f"Error getting account details: {e}")
            return None

    def get_instrument_contract(self):
        try:
            contract = self.api.contracts(dict(symbol=self.symbol, productType='USDT-FUTURES'))
            if contract and 'data' in contract and contract['data']:
                print(f"Contract detail: {contract['data'][0]}")
                return contract['data'][0]
            else:
                return None  # Or raise an exception
        except Exception as e:
            print(f"Error getting contract: {e}")
            return None

    def place_trigger_order(self, side, order_type, price, sl, tp):

        # pending_orders = self.api.ordersPlanPending(dict(symbol=self.symbol, productType='USDT-FUTURES', marginCoin='USDT'))
        # if pending_orders and 'data' in pending_orders and pending_orders['data']:
        #     print(f"Pending orders: {pending_orders['data']}")
        #     return "There are pending orders. Please cancel them before placing a new order."


        # Get the current account balance
        balance = self.get_account_balance()
        if balance is None:
            return "Failed to get account balance"

        size = round(balance * self.risk, self.volume_place)  # Round size to correct precision
        # print(f"Calculated size: {size}")
        # if not self.is_valid_order(size):
        #     raise ValueError(f"Order size {size} is less than the minimum {self.min_trade_num} for {self.symbol}")
        price = round(price, self.price_place) # Round price to correct precision
        tp = round(tp, self.price_place) # Round tp to correct precision
        sl = round(sl, self.price_place) # Round sl to correct precision

        oid = self.oid()  # Generate a unique order ID

        params = {
            "planType": "normal_plan",
            "symbol": self.symbol,
            "productType": "USDT-FUTURES",
            "marginMode": "isolated",
            "marginCoin": "USDT",
            "size": str(size),  # Convert size to string
            "price": str(price), # Convert price to string
            "triggerPrice": str(price),  # Convert price to string
            "triggerType": "mark_price",
            "side": side,
            "tradeSide": "open",
            "orderType": order_type,
            "clientOid": oid,
            "stopSurplusTriggerPrice": str(tp), # Convert tp to string
            "stopSurplusTriggerType": "mark_price",
            "stopLossTriggerPrice": str(sl),  # Convert sl to string
            "stopLossTriggerType": "mark_price"
        }

        # print(f"Placing order: {params}")
        try:
            response = self.api.placePlanOrder(params)
            return response
        except Exception as e:
            print(f"Failed to place order: {e}")

    def is_valid_order(self, amount):
        return amount >= self.min_trade_num

    def trail_stop(self, current_position, price, trailing_sl_trigger_pct, trailing_sl_pct):
        """
        Adjust the trailing stop loss based on price movement for crypto.
        

        """
        sl = current_position['sl']  # Existing stop loss
        entry_price = current_position['openPriceAvg']  # Entry price of the position

        # Trailing stop for BUY position
        if current_position['holdSide'] == 'long':
            bid = price['bid']  # Use the close price as bid price for simplicity
            if (bid - entry_price) > (trailing_sl_trigger_pct * entry_price):  # Trigger condition
                new_sl = bid - (trailing_sl_pct * entry_price)  # Calculate new stop loss
                if new_sl > sl:  # Only update if the new stop loss is higher (to protect profits)
                    current_position['sl'] = new_sl  # Update the stop loss

        # Trailing stop for SELL position
        elif current_position['side'] == 'short':
            ask = price['ask']  # Use the close price as ask price for simplicity
            if (entry_price - ask) > (trailing_sl_trigger_pct * entry_price):  # Trigger condition
                new_sl = ask + (trailing_sl_pct * entry_price)  # Calculate new stop loss
                if new_sl < sl:  # Only update if the new stop loss is lower (to protect profits)
                    current_position['sl'] = new_sl  # Update the stop loss

        return current_position

    def get_all_positions(self, prodcut_type, margin_coin):
        params = {
            "productType": "USDT-FUTURES",
            "marginCoin": "USDT",
        }

        try:
            response = self.api.allPosition(params)
            positions = response['data']
            return positions
        except Exception as e:
            return f"Failed to get all position: {e}"
    
    def get_order_detail(self, symbol, oid):
        params = {
            "symbol": symbol,
            "productType": "USDT-FUTURES",
            "orderId": "",
            "clientOid": oid,
        }

        try:
            response = self.api.detail(params)
            order_detail = response['data']
            return order_detail
        except Exception as e:
            return f"Failed to get order detail: {e}"


    def get_min_order_amount(self, symbol):
        """
        Retrieve the minimum allowable order size for a specific trading pair.

        """
        return self._session.markets_by_id[symbol]["info"]["minProvideSize"]

    def convert_amount_to_precision(self, symbol, amount):
        """
        Format the order amount to the required precision for the given symbol.
        :param symbol: Trading pair symbol, e.g., 'BTCUSDT'.
        :param amount: Desired order amount.
        :return: Amount formatted to the required precision.
        """
        return self._session.amount_to_precision(symbol, amount)

    def convert_price_to_precision(self, symbol, price):
        """
        Format the order price to the required precision for the given symbol.
        :param symbol: Trading pair symbol, e.g., 'BTCUSDT'.
        :param price: Desired order price.
        :return: Price formatted to the required precision.
        """
        return self._session.price_to_precision(symbol, price)

    def is_valid_order(self, symbol, amount):
        """
        Check if the order amount is valid based on the minimum order size.
        :param symbol: Trading pair symbol, e.g., 'BTCUSDT'.
        :param amount: Desired order amount.
        :return: Boolean indicating if the order amount is valid.
        """
        min_amount = float(self.get_min_order_amount(symbol))
        return amount >= min_amount

