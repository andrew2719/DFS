import asyncio

async def handle_client(reader, writer):
    # Connection established
    addr = writer.get_extra_info('peername')
    print(f"Connected with {addr}")

    # Receive data from the client
    data = await reader.read(100)  # Adjust buffer size as needed
    message = data.decode()
    print(f"Received from {addr}: {message}")

    # Send a random message back to the client
    response = f"Hello from the server to {addr}"
    writer.write(response.encode())
    await writer.drain()
    print(f"Sent to {addr}: {response}")

    # Receive the hash from the client
    data = await reader.read(100)  # Adjust buffer size as needed
    message = data.decode()
    print(f"Received from {addr}: {message}")
    # Close the connection
    writer.close()
    await writer.wait_closed()

async def start_server(port):
    server = await asyncio.start_server(handle_client, '0.0.0.0', port)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

async def main():
    port = 12345  # The same port as your client script
    await start_server(port)

asyncio.run(main())
