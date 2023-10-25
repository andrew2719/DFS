import asyncio
import hashlib
import Responses

class Distributor:
    def __init__(self,peer_connections,table):
        self.peers = peer_connections # has ([ip] = (reader,writer))
        self.table = table
        self.MAX_RETRIES = 3
        self.BACKOFF_INITIAL_DELAY = 1  # in seconds
        self.node_metadata = {}
        for i in self.peers:
            self.node_metadata[i] = {'success_rate': 0}
        self.busy_nodes = set()
    
    async def send_chunk_to_peer(self, chunk, expected_hash, ip):
        # This is a mock function for demonstration purposes. Replace with actual sending logic.
        writer = None  # You should create the writer here
        await writer.write(chunk)

        # For demonstration purposes, we'll simulate the hash check
        received_hash = hashlib.sha256(chunk.encode()).hexdigest()

        if received_hash == expected_hash:
            # Just a mock to simulate success rate.
            # Replace this logic with actual communication and validation with the node
            if node_metadata[ip]['success_rate'] > 50:
                return True
            else:
                return False
        return False

    def get_best_available_node(self):
        sorted_peers = sorted(self.peers, key=lambda ip: node_metadata[ip]['success_rate'], reverse=True)
        for peer in sorted_peers:
            if peer not in busy_nodes:
                return peer
        return None

    def distribute_chunk_to_all_peers(self, chunk, expected_hash):
        best_node = self.get_best_available_node()
        if best_node:
            busy_nodes.add(best_node)
            asyncio.create_task(self.distribute_chunk_to_node(chunk, expected_hash, best_node))

    async def distribute_chunk_to_node(self, chunk, expected_hash, ip, retries=0):
        try:
            success = await self.send_chunk_to_peer(chunk, expected_hash, ip)
            if success:
                # Increase success_rate (just a mock, replace with your actual logic)
                node_metadata[ip]['success_rate'] += 5
            else:
                if retries < MAX_RETRIES:
                    await asyncio.sleep(BACKOFF_INITIAL_DELAY * (2 ** retries))
                    await self.distribute_chunk_to_node(chunk, expected_hash, ip, retries + 1)
        finally:
            busy_nodes.remove(ip)

    async def distribute_all_chunks(self, chunks_dict):
        for chunk, expected_hash in chunks_dict.items():
            self.distribute_chunk_to_all_peers(chunk, expected_hash)


def main():
    distributor = Distributor()
    chunks_dict = {
        "chunk1": hashlib.sha256("chunk1".encode()).hexdigest(),
        "chunk2": hashlib.sha256("chunk2".encode()).hexdigest(),
        # ... other chunks
    }

    asyncio.run(distributor.distribute_all_chunks(chunks_dict))


if __name__ == "__main__":
    main()
