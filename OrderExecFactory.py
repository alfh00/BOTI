from abc import ABC, abstractmethod

class OrderExecutor(ABC):
    @abstractmethod
    def execute(self, symbol: str, side: str, price: float, size: float) -> dict:
        pass

class MarketOrderExecutor(OrderExecutor):
    def __init__(self, api: BitgetClient):
        self.api = api

    def execute(self, symbol: str, side: str, price: float, size: float) -> dict:
        return self.api.place_market_order(symbol, side, size)

class LimitOrderExecutor(OrderExecutor):
    def __init__(self, api: BitgetClient):
        self.api = api

    def execute(self, symbol: str, side: str, price: float, size: float) -> dict:
        return self.api.place_limit_order(symbol, side, price, size)

class OrderExecutorFactory:
    @staticmethod
    def get_executor(order_type: str, api: BitgetClient) -> OrderExecutor:
        executors = {
            "market": MarketOrderExecutor(api),
            "limit": LimitOrderExecutor(api),
        }
        return executors.get(order_type.lower())