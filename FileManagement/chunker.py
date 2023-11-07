import asyncio

import hashlib


class Chunker:
    def __init__(self, data):
        self.data = data
        self.n = 4
        self.chunks = {}
        '''{
        'INDEX': int,
        'DATA': bytearray,
        'HASH': None,
        'SIZE': int,
        }'''
        self.hash_table = {}


    async def chunker(self):
        """Divide the data (bytearray) into 'n' chunks."""
        chunk_size = len(self.data) // self.n

        for i in range(self.n):
            chunk = self.data[i * chunk_size: (i + 1) * chunk_size]
            self.chunks[i] = {
                'INDEX': i,
                'DATA': chunk,
                'HASH': None,
                'SIZE': len(chunk),
            }
            self.hash_table[i] = hashlib.sha256(chunk).hexdigest()

        return self.chunks, self.hash_table