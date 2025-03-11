
from .bitget_c.client import Client
from .bitget_c.consts import GET, POST


class BitgetClient(Client):
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, first=False):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, first)
    
    #----------- ACCOUNT -----------#

    def account(self, params):
        return self._request_with_params(GET, '/api/v2/mix/account/account', params)

    def accounts(self, params):
        return self._request_with_params(GET, '/api/v2/mix/account/accounts', params)

    def setLeverage(self, params):
        return self._request_with_params(POST, '/api/v2/mix/account/set-leverage', params)

    def setMargin(self, params):
        return self._request_with_params(POST, '/api/v2/mix/account/set-margin', params)

    def setMarginMode(self, params):
        return self._request_with_params(POST, '/api/v2/mix/account/set-margin-mode', params)

    def setPositionMode(self, params):
        return self._request_with_params(POST, '/api/v2/mix/account/set-position-mode', params)

    def openCount(self, params):
        return self._request_with_params(GET, '/api/v2/mix/account/open-count', params)

    def singlePosition(self, params):
        return self._request_with_params(GET, '/api/v2/mix/position/single-position', params)

    def allPosition(self, params):
        return self._request_with_params(GET, '/api/v2/mix/position/all-position', params)
    
    #----------- MARKET -----------#

    def contracts(self, params):
        return self._request_with_params(GET, '/api/v2/mix/market/contracts', params)

    def orderbook(self, params):
        return self._request_with_params(GET, '/api/v2/mix/market/orderbook', params)

    def tickers(self, params):
        return self._request_with_params(GET, '/api/v2/mix/market/tickers', params)

    def fills(self, params):
        return self._request_with_params(GET, '/api/v2/mix/market/fills', params)

    def candles(self, params):
        return self._request_with_params(GET, '/api/v2/mix/market/candles', params)
    
    #----------- ORDER -----------#

    def placeOrder(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/place-order', params)

    def clickBackhand(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/click-backhand', params)

    def batchPlaceOrder(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/batch-place-order', params)

    def cancelOrder(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/cancel-order', params)

    def batchCancelOrders(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/batch-cancel-orders', params)

    def closePositions(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/close-positions', params)

    def ordersHistory(self, params):
        return self._request_with_params(GET, '/api/v2/mix/order/orders-history', params)

    def ordersPending(self, params):
        return self._request_with_params(GET, '/api/v2/mix/order/orders-pending', params)

    def detail(self, params):
        return self._request_with_params(GET, '/api/v2/mix/order/detail', params)

    def fills(self, params):
        return self._request_with_params(GET, '/api/v2/mix/order/fills', params)

    def placePlanOrder(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/place-plan-order', params)

    def cancelPlanOrder(self, params):
        return self._request_with_params(POST, '/api/v2/mix/order/cancel-plan-order', params)

    def ordersPlanPending(self, params):
        return self._request_with_params(GET, '/api/v2/mix/order/orders-plan-pending', params)

    def ordersPlanHistory(self, params):
        return self._request_with_params(GET, '/api/v2/mix/order/orders-plan-history', params)

    def traderOrderClosePositions(self, params):
        return self._request_with_params(POST, '/api/v2/copy/mix-trader/order-close-positions', params)

    def traderOrderCurrentTrack(self, params):
        return self._request_with_params(GET, '/api/v2/copy/mix-trader/order-current-track', params)

    def traderOrderHistoryTrack(self, params):
        return self._request_with_params(GET, '/api/v2/copy/mix-trader/order-history-track', params)
    

