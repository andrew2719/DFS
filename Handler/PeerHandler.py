import asyncio
import random


class DataDistributor:
    def __init__(self, peers):
        self.peers = peers  # Dictionary with {ip: (reader, writer)}
        self.locks = {ip: asyncio.Lock() for ip in peers}
        self.MAX_RETRIES = 3
        self.BACKOFF_INITIAL_DELAY = 1
        self.BACKOFF_FACTOR = 2
        self.MAX_BACKOFF = 60

    async def send_initial_ack(self, reader, writer, data):
        # Your ACK sending implementation here
        pass

    async def send_data_to_node(self, writer, idx, data):
        # Your data sending implementation here
        pass

    def calculate_backoff_delay(self, attempt):
        return min(self.MAX_BACKOFF, random.uniform(self.BACKOFF_INITIAL_DELAY, self.BACKOFF_FACTOR ** attempt))

    async def distribute_chunk_to_node(self, idx, data):
        nodes_tried = set()  # Keep track of nodes that have been tried
        while len(nodes_tried) < len(self.peers):
            for ip, lock in self.locks.items():
                if ip in nodes_tried:
                    continue  # Skip nodes that we've already tried the max number of times

                try:
                    async with lock:
                        reader, writer = self.peers[ip]
                        for attempt in range(1, self.MAX_RETRIES + 1):
                            try:
                                ack_received = await self.send_initial_ack(reader, writer, data)
                                if ack_received:
                                    sending_status = await self.send_data_to_node(writer, idx, data)
                                    if sending_status:
                                        self.lookup_table[idx] = ip  # Track where the data was sent
                                        return True  # Data was successfully sent
                            except Exception as e:
                                print(f"Error sending data to node {ip} on attempt {attempt}: {e}")
                                if attempt == self.MAX_RETRIES:
                                    nodes_tried.add(ip)  # Add to nodes tried after reaching max retries
                                    break  # Move to the next node after max retries
                                backoff_delay = self.calculate_backoff_delay(attempt)
                                await asyncio.sleep(backoff_delay)
                        break  # Break after attempting to send to the current node
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    print(f"An unexpected error occurred with node {ip}: {e}")
                finally:
                    await asyncio.sleep(0.01)  # Small sleep to prevent busy looping

        return False  # If all nodes have been tried and data has not been sent


async def main():
    # Example peers structure
    peers = {
        'peer1': (None, None),  # Replace with actual reader and writer objects
        'peer2': (None, None),
        # ... more peers ...
    }

    distributor = DataDistributor(peers)

    # Example of distributing data
    tasks = [distributor.distribute_chunk_to_node(idx, data)
             for idx, data in enumerate(["data1", "data2", "data3"])]  # Replace with actual data

    results = await asyncio.gather(*tasks)
    print(results)  # This will show which tasks were successful and which were not


asyncio.run(main())
