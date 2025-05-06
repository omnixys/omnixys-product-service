# src/product/dev_server.py

import asyncio
from watchfiles import awatch
from hypercorn.asyncio import serve
from hypercorn.config import Config
from product.config.tls import tls_certfile, tls_keyfile
from product.fastapi_app import app


async def start_server():
    config = Config()
    config.bind = ["127.0.0.1:8002"]
    config.certfile = tls_certfile
    config.keyfile = tls_keyfile
    config.use_reloader = False


    await serve(app, config)


async def run_dev_server():
    while True:
        task = asyncio.create_task(start_server())
        async for _ in awatch("src/product"):
            print("🔁 Änderungen erkannt, Server wird neu gestartet…")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


def main():
    asyncio.run(run_dev_server())
