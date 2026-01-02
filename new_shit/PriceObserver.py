from abc import ABC, abstractmethod
from typing import List

# Observer Interface
class PriceObserver(ABC):
    @abstractmethod
    def update(self, price: float):
        pass

# Subject (Observable)
class PriceStreamer:
    def __init__(self):
        self._observers: List[PriceObserver] = []
        self._price = 0.0

    def add_observer(self, observer: PriceObserver):
        self._observers.append(observer)

    def remove_observer(self, observer: PriceObserver):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update(self._price)

    def set_price(self, price: float):
        self._price = price
        self.notify_observers()

# Concrete Observer
class PriceProcessor(PriceObserver):
    def __init__(self, name: str):
        self._name = name

    def update(self, price: float):
        print(f"{self._name} received new price: {price}")
        # Add processing logic here (e.g., filtering, normalization, etc.)

# Example Usage
if __name__ == "__main__":
    # Create the PriceStreamer (subject)
    price_streamer = PriceStreamer()

    # Create the PriceProcessor (observer)
    price_processor = PriceProcessor("Processor1")

    # Register the observer with the subject
    price_streamer.add_observer(price_processor)

    # Simulate price updates
    price_streamer.set_price(100.50)  # Processor1 receives new price: 100.50
    price_streamer.set_price(101.00)  # Processor1 receives new price: 101.00