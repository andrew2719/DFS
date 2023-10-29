import asyncio
import hashlib

class Distributor:
    def __init__(self, peer_connections):
        self.peers = peer_connections
        self.MAX_RETRIES = 3
        self.BACKOFF_INITIAL_DELAY = 1  # in seconds
        self.node_metadata = {}
        for ip, (reader, writer) in self.peers.items():
            self.node_metadata[ip] = {'success_rate': 0, 'retries': 0}
        self.busy_nodes = {ip: False for ip in self.peers.keys()}
        # self.table = None

    def get_backoff_delay(self, attempt):
        return min(self.MAX_RETRIES, self.BACKOFF_INITIAL_DELAY * (2 ** attempt))

    async def distribute_chunk_to_node(self, idx, data):
        attempt = 0
        while attempt < self.MAX_RETRIES:
            available_nodes = [ip for ip, is_busy in self.busy_nodes.items() if not is_busy]
            if not available_nodes:
                await asyncio.sleep(self.BACKOFF_INITIAL_DELAY)
                continue

            ip = available_nodes[0]
            reader, writer = self.peers[ip]
            self.busy_nodes[ip] = True

            try:
                ack_received = await self.send_initial_ack(reader, writer, data)
                if ack_received:
                    await self.send_data_to_node(writer, idx, data)
                    break
                else:
                    self.node_metadata[ip]['retries'] += 1
                    delay = self.get_backoff_delay(attempt)
                    await asyncio.sleep(delay)
                    attempt += 1
            finally:
                self.busy_nodes[ip] = False

    async def send_initial_ack(self, reader, writer, data):
        size = len(data)
        message = f"type:upload,size:{size}"
        writer.write(message.encode())
        await writer.drain()
        response = await reader.readline()
        expected_hash = hashlib.sha256(str(size).encode()).hexdigest()

        return response.decode().strip() == expected_hash

    async def send_data_to_node(self, writer, idx, data):
        writer.write(data.encode())
        await writer.drain()

    async def distribute_to_nodes(self, data_table):
        tasks = [self.distribute_chunk_to_node(idx, data) for idx, data in data_table.items()]
        await asyncio.gather(*tasks)
    async def distribute(self,data_table):
        self.table = {}
        for i in data_table:
            self.table[i] = {}
            for j in data_table[i]:
                if j == "DATA":
                    self.table[i][j] = base64.b64encode(data_table[i][j]).decode()

# Example usage
peer_connections = {
'192.168.1.1': (None, None),  # dummy (reader, writer) for now
'192.168.1.2': (None, None)
}

distributor = Distributor(peer_connections)
data_table = {
1: 'data1',
2: 'data2',
3: 'data3'
}

# To distribute the chunks
# asyncio.run(distributor.distribute_to_nodes(data_table))
