import asyncio
import websockets


async def connect_to_websocket():
    url = "wss://realtime.ably.io/?access_token=f6emEQ.Ih1whkfwt_SHy0-wDseNKElB2Ku7-C_hMCO7IwWYkkYWANjTlz3OmPtnJ4k-R0CmHjT5AM8vrIHXCR62Oq6-oOdaZKN_26FYD4TQH7LNkxdsk51chxHBRvGRvwHIyfBqmJ7Pq-utdpv18zzTXRdLtKYmfll-8lk5TfQYFcpbAUa0qmBBuK0u1vkpaHC6s619e6IA7Z3nJzxQfeg_UipX1gUQvRHzF_bOD3VQnVAg17lE&recover=a2dnopbIABh2T6!PdDoEF6CNhAT0PfzNZOQJ3-26b99e&format=json&heartbeats=true&v=2&agent=ably-js%2F1.2.50%20browser"

    async with websockets.connect(url) as websocket:
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")


# Run the WebSocket connection
asyncio.get_event_loop().run_until_complete(connect_to_websocket())
