import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        r = await client.get('http://localhost:8000/health')
        print(f"Health Status: {r.status_code}")
        print(f"Body: {r.text[:200]}")

asyncio.run(test())
