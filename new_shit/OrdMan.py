class OrderManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, api: BitgetClient):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.api = api
                cls._instance.risk_manager = RiskManager(api)
                cls._instance.order_queue = queue.Queue()
                cls._instance.shutdown_event = threading.Event()
                cls._instance.logger = logging.getLogger("OrderManager")
                cls._instance.thread = threading.Thread(target=cls._instance._process_orders, daemon=True)
                cls._instance.thread.start()
            return cls._instance

    def place_order(self, symbol: str, order_type: str, side: str, price: float, risk_pct: float):
        """Add an order to the queue after risk validation."""
        try:
            size = self.risk_manager.calculate_position_size(symbol, risk_pct)
            self.order_queue.put({
                "symbol": symbol,
                "order_type": order_type,
                "side": side,
                "price": price,
                "size": size,
            })
        except Exception as e:
            self.logger.error(f"Order rejected by RiskManager: {e}")

    def _process_orders(self):
        """Process orders from the queue using the appropriate executor."""
        while not self.shutdown_event.is_set():
            try:
                order = self.order_queue.get(timeout=1)
                executor = OrderExecutorFactory.get_executor(order["order_type"], self.api)
                if executor:
                    response = executor.execute(order["symbol"], order["side"], order["price"], order["size"])
                    self.logger.info(f"Order executed: {response}")
                else:
                    self.logger.error(f"Unsupported order type: {order['order_type']}")
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Order failed: {e}")

    def shutdown(self):
        self.shutdown_event.set()
        self.thread.join()