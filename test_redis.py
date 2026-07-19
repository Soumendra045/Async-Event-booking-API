import asyncio


from app.core.redis import redis_client

async def main():
    result = await redis_client.ping()
    print(result)

asyncio.run(main())

