from thread_base import ThreadBase
from models.live_position import LivePosition
import threading
import copy

class PositionProcessor(ThreadBase):
    def __init__(self, shared_positions, position_lock: threading.Lock, position_events, position_queue, logname, pair, shutdown_event):
        super().__init__(logname=logname, shared=shared_positions, lock=position_lock, events=position_events)
        self.pair = pair
        self.position_queue = position_queue
        self.shutdown_event = shutdown_event
        
    def update_position(self, position: LivePosition):
        self.position_queue.put(position)

    def process_position(self):
        try:
            self.lock.acquire()
            position = copy.deepcopy(self.shared[self.pair])      
            self.update_position(position)

        except Exception as e:
            self.log_message(f'CRASH : {e}', error=True)
        finally:
            self.lock.release()

    def run(self):
        while not self.shutdown_event.is_set():
            self.events[self.pair].wait()
            self.process_position()
            self.events[self.pair].clear()
        print(f"{self.name} is shutting down gracefully.")

