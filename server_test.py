import asyncio
import random
async def check_port(ip, port):
    """Attempt to connect to the specified IP and port, and return the connection if successful."""
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        return ip, (reader, writer)
    except Exception as e:
        print(f"Failed to connect to {ip}:{port} - {e}")
        return None

async def scan_specific_range(start_ip, end_ip, port):
    """Scan a specific range of IP addresses and return open connections."""
    start_segment = int(start_ip.split('.')[-1])
    end_segment = int(end_ip.split('.')[-1])
    base_ip = '.'.join(start_ip.split('.')[:-1])

    tasks = []
    for i in range(start_segment, end_segment + 1):
        ip = f"{base_ip}.{i}"
        tasks.append(check_port(ip, port))

    results = await asyncio.gather(*tasks)
    return {ip: conn for result in results if result is not None for ip, conn in [result]}

async def scan_network(port, ranges):
    """Scan multiple ranges for hosts listening on the given port and return open connections."""
    all_connections = {}
    for range_info in ranges:
        connections = await scan_specific_range(range_info['start_ip'], range_info['end_ip'], port)
        all_connections.update(connections)
    return all_connections

async def send_message_to_all(connections, message):
    """Send a message to all established connections."""
    for ip, (reader, writer) in connections.items():
        print(f"Sending to {ip}: {message}")
        writer.write(message.encode())
        await writer.drain()
        received = await reader.read(100)
        print(f"Received from {ip}: {received.decode()}")

        random_hash = random.getrandbits(128)
        writer.write(str(random_hash).encode())
        await writer.drain()


async def main():
    target_port = 12345  # Example port
    ranges = [
        {"start_ip": "192.168.29.1", "end_ip": "192.168.29.255"},
        {"start_ip": "127.0.0.1", "end_ip": "127.0.0.1"}
    ]

    print("Scanning the network and establishing connections...")
    connections = await scan_network(target_port, ranges)
    print(f"Established connections: {list(connections.keys())}")

    if connections:
        random_message = "Random message from client"
        await send_message_to_all(connections, random_message)

        for _, (reader, writer) in connections.items():
            writer.close()
            await writer.wait_closed()
    else:
        print("No connections were established.")

asyncio.run(main())
