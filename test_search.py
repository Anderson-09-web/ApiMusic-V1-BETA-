import asyncio
import wavelink

async def main():
    node = wavelink.Node(
        identifier="test",
        uri="http://127.0.0.1:8080",
        password="musicapi"
    )

    await node._session.close()

    print("✅ Node creado correctamente")

asyncio.run(main())
