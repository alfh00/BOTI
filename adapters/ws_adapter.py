
import asyncio

from apis.BitgetWSClient import BitgetWSClient

async def main():
    # Initialize client (for public channels only)
    public_client = BitgetWSClient()
    
    # For private channels:
    # private_client = BitgetWSClient(
    #     api_key="your_api_key",
    #     api_secret="your_api_secret",
    #     passphrase="your_passphrase"
    # )
    
    # Define callbacks
    async def ticker_callback(data):
        print(f"Ticker update: {data}")

    async def candle_callback(data):
        print(f"Candle update: {data}")
    
    # Use context manager for connection handling
    async with public_client:
        # Subscribe to channels with callbacks
        await public_client.subscribe(
            ["orders-algo:USDT-FUTURES:BTCUSDT", "candle5m:SPOT:BTCUSDT"],
            ticker_callback  # Same callback for both channels in this example
        )
        
        # Run for 60 seconds
        await asyncio.sleep(60)
        
        # Unsubscribe when done
        await public_client.unsubscribe(["ticker:SPOT:BTCUSDT"])

if __name__ == "__main__":
    asyncio.run(main())