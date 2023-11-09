import asyncio
import random
# from Responses import ReadWrite
from . import Responses
import json
from FileManagement import chunker
import hashlib
from DFS_main.logger import logger

class DataDistributor:
    def __init__(self, peers):
        self.peers = peers  # Dictionary with {ip: (reader, writer)}
        self.locks = {ip: asyncio.Lock() for ip in peers}
        self.MAX_RETRIES = 3
        self.BACKOFF_INITIAL_DELAY = 1
        self.BACKOFF_FACTOR = 2
        self.MAX_BACKOFF = 60

    async def send_initial_ack(self,read_write_obj,data):
        inital_ack = {
            'NODE':'PEER',
            'TYPE': 'UPLOAD',
            'SIZE': data
        }
        inital_ack = json.dumps(inital_ack).encode()
        await read_write_obj.write_(inital_ack)

        ack_received = await read_write_obj.read_in_loop()
        logger.info("from PeerHandler.py ack is : " + str(ack_received))
        ack_received = json.loads(ack_received.decode())
        return ack_received['status']

    async def send_data_to_node(self,read_in_loop,write_in_loop, data):
        await write_in_loop(data)

        response_hash = await read_in_loop()

        hash = hashlib.sha256(data).hexdigest()

        if hash == response_hash.decode():
            logger.info("from PeerHandler.py : Hash matched")
            await write_in_loop("True".encode())
            save_status = await read_in_loop()
            save_status = json.loads(save_status.decode())

            if save_status['status']==True:
                logger.info("File saved successfully")
                return True,hash
            else:
                logger.error(save_status)
                return False,None
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
                        logger.info(f"Sending chunk to node {ip}")
                        read_write_obj = Responses.ReadWrite(reader, writer)
                        read_in_loop = Responses.ReadWrite(reader, writer).read_in_loop()
                        write_in_loop = Responses.ReadWrite(reader, writer)
                        for attempt in range(1, self.MAX_RETRIES + 1):
                            try:
                                size = len(chunk_info['DATA'])
                                ack_received = await self.send_initial_ack(read_write_obj, size)
                                logger.info("from PeerHandler.py : " + str(ack_received))
                                if ack_received:
                                    sending_status,hash = await self.send_data_to_node(read_in_loop,write_in_loop, chunk_info['DATA'])

                                    if sending_status:
                                        chunk_info['SENT_TO'] = ip  # Record where the data was sent
                                        chunk_info['HASH'] = hash
                                        return True  # Data was successfully sent
                            except Exception as e:
                                # print(f"Error sending data to node {ip} on attempt {attempt}: {e}")
                                logger.error(f"Error sending data to node {ip} on attempt {attempt}: {e}")
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

        # Check if any of the tasks failed if any failed return false else return true
        for result in results:
            if not result:
                return False
        return True



    async def distribute(self, data):
        table, hash_table = await chunker.Chunker(data).chunker()
        logger.info("from PeerHandler.py : " + str(table),str(hash_table))
        sent_status = await self.distribute_to_nodes(table)
        final_table = table
        return final_table,sent_status