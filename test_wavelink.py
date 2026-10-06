import asyncio
import wavelink

async def main():
    node = wavelink.Node(
        identifier="local",
        uri="http://127.0.0.1:8080",
        password="musicapi"
    )

    print("✅ Node creado:", node.identifier)

    await node._session.close()

asyncio.run(main())
