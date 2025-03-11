from datetime import datetime, timezone
import pytz

class LiveStreamPrice:
    def __init__(self, data):
        self.time = datetime.fromtimestamp(data.get("ts")/1000, tz=pytz.timezone('UTC'))
        self.symbol = data.get('symbol')   
        self.price = float(data.get('price'))  
        self.ask = float(data.get('ask')) 
        self.bid = float(data.get('bid'))
        self.volume = float(data.get('volume'))

    def __repr__(self):
        return (f"LiveStreamPrice() {self.time},  {self.symbol}, price : {self.price}, "
                f"ask: {self.ask}, bid: {self.bid}, volume: {self.volume})")