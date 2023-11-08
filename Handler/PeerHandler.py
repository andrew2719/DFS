import asyncio
import random
from Responses import ReadWrite
import json
from FileManagement import chunker
import hashlib

class DataDistributor:
    def __init__(self, peers):
        self.peers = peers  # Dictionary with {ip: (reader, writer)}
        self.locks = {ip: asyncio.Lock() for ip in peers}
        self.MAX_RETRIES = 3
        self.BACKOFF_INITIAL_DELAY = 1
        self.BACKOFF_FACTOR = 2
        self.MAX_BACKOFF = 60

    async def send_initial_ack(self,read_in_loop, write_in_loop, data):
        inital_ack = {
            'TYPE': 'INITIAL_ACK',
            'size': data
        }
        inital_ack = json.dumps(inital_ack).encode()
        await write_in_loop(inital_ack)

        ack_received = await read_in_loop()
        ack_received = json.loads(ack_received.decode())
        return ack_received['status']

    async def send_data_to_node(self,read_in_loop,write_in_loop, data):
        await write_in_loop(data)

        response_hash = await read_in_loop()

        hash = hashlib.sha256(data).hexdigest()

        if hash == response_hash.decode():
            return True,hash
        else:
            return False,None


    def calculate_backoff_delay(self, attempt):
        return min(self.MAX_BACKOFF, random.uniform(self.BACKOFF_INITIAL_DELAY, self.BACKOFF_FACTOR ** attempt))

    async def distribute_chunk_to_node(self, chunk_info):
        nodes_tried = set()  # Keep track of nodes that have been tried

        while len(nodes_tried) < len(self.peers):
            for ip, lock in self.locks.items():
                if ip in nodes_tried:
                    continue  # Skip nodes that we've already tried the max number of times

                try:
                    async with lock:
                        reader, writer = self.peers[ip]
                        read_in_loop = ReadWrite(reader, writer).read_in_loop()
                        write_in_loop = ReadWrite(reader, writer)
                        for attempt in range(1, self.MAX_RETRIES + 1):
                            try:
                                size = len(chunk_info['DATA'])
                                ack_received = await self.send_initial_ack(read_in_loop,write_in_loop, size)
                                if ack_received:
                                    sending_status,hash = await self.send_data_to_node(read_in_loop,write_in_loop, chunk_info['DATA'])
                                    if sending_status:
                                        chunk_info['SENT_TO'] = ip  # Record where the data was sent
                                        chunk_info['HASH'] = hash
                                        return True  # Data was successfully sent
                            except Exception as e:
                                print(f"Error sending data to node {ip} on attempt {attempt}: {e}")
                                if attempt == self.MAX_RETRIES:
                                    nodes_tried.add(ip)  # Add to nodes tried after reaching max retries
                                    break  # Move to the next node after max retries
                                backoff_delay = self.calculate_backoff_delay(attempt)
                                await asyncio.sleep(backoff_delay)

                        break
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    print(f"An unexpected error occurred with node {ip}: {e}")
                finally:
                    await asyncio.sleep(0.01)

        return False

    async def distribute_to_nodes(self, table):
        tasks = [self.distribute_chunk_to_node(chunk_info) for chunk_info in table.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    async def distribute(self, data):
        table, hash_table = await chunker.Chunker(data).chunker()
        await self.distribute_to_nodes(table)
        final_table = table
        return final_table