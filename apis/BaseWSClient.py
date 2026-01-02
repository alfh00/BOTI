import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set
import websockets
from websockets.exceptions import ConnectionClosed

class BaseWSClient(ABC):
    """
    Abstract base class for WebSocket clients.
    Handles core WebSocket functionality with asyncio.
    """
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.subscriptions: Set[str] = set()
        self.callbacks: Dict[str, Callable] = {}
        self._keepalive_task = None
        self._message_handler_task = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def ws_url(self) -> str:
        """WebSocket endpoint URL"""
        pass

    @abstractmethod
    async def authenticate(self):
        """Authenticate with the WebSocket server"""
        pass

    @abstractmethod
    def get_keepalive_message(self) -> Any:
        """Get the keepalive/ping message for this connection"""
        pass

    @abstractmethod
    def is_keepalive_message(self, message: str) -> bool:
        """Check if a message is a keepalive/ping message"""
        pass

    async def connect(self):
        """Establish WebSocket connection"""
        if self.connected:
            return

        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            self._reconnect_attempts = 0
            self.logger.info("WebSocket connected")

            # Authenticate if needed
            await self.authenticate()

            # Start background tasks
            self._keepalive_task = asyncio.create_task(self._keepalive())
            self._message_handler_task = asyncio.create_task(self._handle_messages())

        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            await self._handle_reconnect()

    async def disconnect(self):
        """Close WebSocket connection"""
        if not self.connected:
            return

        self.connected = False
        
        if self._keepalive_task:
            self._keepalive_task.cancel()
        if self._message_handler_task:
            self._message_handler_task.cancel()

        if self.websocket:
            await self.websocket.close()
            self.logger.info("WebSocket disconnected")

    async def send(self, message: Any):
        """Send a message through the WebSocket"""
        if not self.connected:
            raise ConnectionError("WebSocket is not connected")

        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            await self.websocket.send(message)
        except ConnectionClosed:
            self.logger.warning("Connection closed while sending message")
            await self._handle_reconnect()
            raise

    async def subscribe(self, channels: List[str], callback: Optional[Callable] = None):
        """
        Subscribe to channels
        :param channels: List of channel names to subscribe to
        :param callback: Optional callback function for these channels
        """
        raise NotImplementedError("Subclass must implement subscribe method")

    async def unsubscribe(self, channels: List[str]):
        """Unsubscribe from channels"""
        raise NotImplementedError("Subclass must implement unsubscribe method")

    async def _keepalive(self):
        """Maintain connection by sending periodic keepalive messages"""
        try:
            while self.connected:
                await asyncio.sleep(30)  # Send every 30 seconds
                if self.connected:
                    try:
                        await self.send(self.get_keepalive_message())
                    except ConnectionError:
                        break
        except asyncio.CancelledError:
            pass

    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    if self.is_keepalive_message(message):
                        continue

                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError:
                    self.logger.warning(f"Received non-JSON message: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {str(e)}")

        except ConnectionClosed as e:
            self.logger.warning(f"WebSocket connection closed: {e}")
            await self._handle_reconnect()
        except Exception as e:
            self.logger.error(f"Error in message handler: {str(e)}")
            await self._handle_reconnect()

    async def _process_message(self, data: Dict):
        """Process incoming message and call appropriate callback"""
        channel = self._get_message_channel(data)
        if channel and channel in self.callbacks:
            try:
                await self.callbacks[channel](data)
            except Exception as e:
                self.logger.error(f"Callback error for {channel}: {str(e)}")

    def _get_message_channel(self, data: Dict) -> Optional[str]:
        """Extract channel name from message data"""
        # Default implementation - can be overridden by subclasses
        return data.get("arg", {}).get("channel")

    async def _handle_reconnect(self):
        """Handle reconnection logic"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            return

        self.connected = False
        self._reconnect_attempts += 1
        delay = min(self._reconnect_delay * self._reconnect_attempts, 30)
        
        self.logger.info(f"Attempting to reconnect in {delay} seconds...")
        await asyncio.sleep(delay)
        
        try:
            await self.connect()
            # Resubscribe to channels after reconnecting
            if self.subscriptions:
                await self.subscribe(list(self.subscriptions))
        except Exception as e:
            self.logger.error(f"Reconnection failed: {str(e)}")
            await self._handle_reconnect()

    def register_callback(self, channel: str, callback: Callable):
        """Register a callback for a specific channel"""
        self.callbacks[channel] = callback

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()