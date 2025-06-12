import os

import aiohttp
from aiokafka import AIOKafkaProducer
from motor.motor_asyncio import AsyncIOMotorClient

from product.config.env import env
from product.health.health_env import health_settings


async def check_kafka():
    try:
        producer = AIOKafkaProducer(bootstrap_servers=env.KAFKA_URI)
        await producer.start()
        await producer.stop()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "down", "message": str(e)}


def check_cert(filename: str):
    path = os.path.join(env.KEYS_PATH, filename)
    try:
        if not os.path.exists(path):
            return {"status": "down", "message": "missing"}
        with open(path, "rb") as f:
            f.read()
        return {"status": "ok"}
    except Exception:
        return {"status": "down", "message": "unreadable"}


async def check_http(name: str, url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as resp:
                if resp.status == 200:
                    return {name: {"status": "ok"}}
                return {name: {"status": "down", "code": resp.status}}
    except Exception as e:
        return {name: {"status": "down", "message": str(e)}}


async def check_mongodb():
    try:
        client = AsyncIOMotorClient(
            health_settings.MONGODB_HEALTH_URL, serverSelectionTimeoutMS=1000
        )
        await client.admin.command("ping")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "down", "message": str(e)}
