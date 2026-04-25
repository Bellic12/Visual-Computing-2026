import asyncio
import json
import random
from datetime import datetime, timezone

import websockets
from websockets.exceptions import ConnectionClosed

HOST = "localhost"
PORT = 8765
SEND_INTERVAL_SECONDS = 0.5
COLORS = ["red", "green", "blue"]


def build_payload() -> dict:
    return {
        "x": round(random.uniform(-4.5, 4.5), 3),
        "y": round(random.uniform(-2.5, 2.5), 3),
        "color": random.choice(COLORS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def handler(websocket):
    client = websocket.remote_address
    print(f"[connect] {client}")
    try:
        while True:
            payload = build_payload()
            await websocket.send(json.dumps(payload))
            await asyncio.sleep(SEND_INTERVAL_SECONDS)
    except ConnectionClosed:
        print(f"[disconnect] {client}")


async def main() -> None:
    print(f"WebSocket server listening on ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
