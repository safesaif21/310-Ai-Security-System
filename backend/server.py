import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)

CONNECTED_CLIENTS = set()

async def register(websocket):
    """Adds a new client to the set of connected clients."""
    CONNECTED_CLIENTS.add(websocket)
    logging.info(f"{websocket.remote_address} connected. Total clients: {len(CONNECTED_CLIENTS)}")

async def unregister(websocket):
    """Removes a client from the set of connected clients."""
    CONNECTED_CLIENTS.remove(websocket)
    logging.info(f"{websocket.remote_address} disconnected. Total clients: {len(CONNECTED_CLIENTS)}")

async def broadcast(message):
    """Sends a message to all connected clients."""
    if CONNECTED_CLIENTS:
        websockets.broadcast(CONNECTED_CLIENTS, message)

async def connection_handler(websocket):
    """
    Handles a new WebSocket connection. It registers the client,
    listens for incoming messages, and unregisters on disconnection.
    """
    await register(websocket)
    try:
        async for message in websocket:
            logging.info(f"Received message from {websocket.remote_address}")
            
            processed_data = "Frame received and processed."
            
            await broadcast(processed_data)

    except websockets.exceptions.ConnectionClosedError:
        logging.info(f"Connection closed unexpectedly by {websocket.remote_address}")
    finally:
        await unregister(websocket)

async def main():
    """Starts the WebSocket server."""
    host = "localhost"
    port = 8765
    async with websockets.serve(connection_handler, host, port):
        logging.info(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server is shutting down.")