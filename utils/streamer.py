from httpx import AsyncClient


class Streamer:
    @staticmethod
    async def receive_file(url):
        async with AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)

            async for dataBytes in response.aiter_bytes():
                yield dataBytes

    @staticmethod
    async def receive_stream(url):
        async with AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                async for dataBytes in response.aiter_bytes():
                    yield dataBytes
