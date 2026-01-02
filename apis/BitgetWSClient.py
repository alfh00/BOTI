import base64
import hashlib
import hmac
import time
from typing import Any, Callable, List, Optional
from apis.BaseWSClient import BaseWSClient

class BitgetWSClient(BaseWSClient):
    """
    Bitget WebSocket client implementation.
    Handles Bitget-specific protocol and message formats.
    """
    
    PUBLIC_WS_URL = "wss://ws.bitget.com/v2/ws/public"
    PRIVATE_WS_URL = "wss://ws.bitget.com/v2/ws/private"
    
    def __init__(self, api_key: str = None, api_secret: str = None, passphrase: str = None):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self._private = bool(api_key and api_secret and passphrase)

    @property
    def ws_url(self) -> str:
        return self.PRIVATE_WS_URL if self._private else self.PUBLIC_WS_URL

    async def authenticate(self):
        """Authenticate with Bitget's private WebSocket"""
        if not self._private:
            return

        timestamp = str(int(time.time()))
        sign = self._generate_signature(timestamp)
        
        auth_msg = {
            "op": "login",
            "args": [{
                "apiKey": self.api_key,
                "passphrase": self.passphrase,
                "timestamp": timestamp,
                "sign": sign
            }]
        }
        
        await self.send(auth_msg)
        self.logger.info("Authentication sent")

    def _generate_signature(self, timestamp: str) -> str:
        """Generate Bitget signature for authentication"""
        message = timestamp + "GET" + "/user/verify"
        hmac_key = bytes(self.api_secret, 'utf-8')
        message_bytes = bytes(message, 'utf-8')
        
        signature = hmac.new(hmac_key, message_bytes, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    def get_keepalive_message(self) -> Any:
        """Bitget uses 'ping' as keepalive"""
        return "ping"

    def is_keepalive_message(self, message: str) -> bool:
        """Check if message is a Bitget keepalive message"""
        return message == "pong" or message == "ping"

    async def subscribe(self, channels: List[str], callback: Optional[Callable] = None):
        """Subscribe to Bitget channels"""
        if not self.connected:
            await self.connect()

        # Bitget requires specific subscription format
        args = []
        for channel in channels:
            # Parse channel format: "channel:instType:instId" or just "channel"
            parts = channel.split(':')
            channel_name = parts[0]
            inst_type = parts[1] if len(parts) > 1 else None
            inst_id = parts[2] if len(parts) > 2 else None
            
            arg = {"channel": channel_name}
            if inst_type:
                arg["instType"] = inst_type
            if inst_id:
                arg["instId"] = inst_id
                
            args.append(arg)
            
            # Store simplified channel name for callback routing
            self.subscriptions.add(channel_name)
            if callback:
                self.callbacks[channel_name] = callback

        sub_msg = {"op": "subscribe", "args": args}
        await self.send(sub_msg)
        self.logger.info(f"Subscribed to channels: {channels}")

    async def unsubscribe(self, channels: List[str]):
        """Unsubscribe from Bitget channels"""
        if not self.connected:
            return

        args = []
        for channel in channels:
            parts = channel.split(':')
            channel_name = parts[0]
            inst_type = parts[1] if len(parts) > 1 else None
            inst_id = parts[2] if len(parts) > 2 else None
            
            arg = {"channel": channel_name}
            if inst_type:
                arg["instType"] = inst_type
            if inst_id:
                arg["instId"] = inst_id
                
            args.append(arg)
            self.subscriptions.discard(channel_name)
            self.callbacks.pop(channel_name, None)

        unsub_msg = {"op": "unsubscribe", "args": args}
        await self.send(unsub_msg)
        self.logger.info(f"Unsubscribed from channels: {channels}")