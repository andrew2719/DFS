# SelfHandler.py

import asyncio
import random
import json
import hashlib
from DFS_main.logger import logger
import base64
from . import Responses

class SelfHandle:
    def __init__(self, reader, writer, file_info, peer_connections):
        self.reader = reader
        self.writer = writer
        self.file_info = file_info
        self.peer_connections = peer_connections

        self.table = b''
        self.chunk_size = 1024
        self.hash_table = {}
        self.read_in_loop, self.write_ = (Responses.ReadWrite(self.reader, self.writer).read_in_loop,
                                          Responses.ReadWrite(self.reader, self.writer).write_)
        self.write_in_loop = Responses.ReadWrite(self.reader,self.writer).write_in_loop


    async def read_look_up_table(self):

        logger.info("reading the table")

        self.table = await self.read_in_loop()

        self.table = json.loads(self.table.decode())
        # logger.info(self.table)
        logger.info("table read, length of the table is : " + str(len(self.table)))

        self.hash_table = {}
        for i in self.table:
            self.table[i]['DATA'] = base64.b64decode(self.table[i]['DATA'].encode())
            self.hash_table[i] = hashlib.sha256(self.table[i]['DATA']).hexdigest()


        self.hash_table = json.dumps(self.hash_table).encode()

        logger.info(json.loads(self.hash_table.decode()))

        await self.write_in_loop(self.hash_table)

        further = await self.read_in_loop()
        further = further.decode()

        logger.info(further)

        # make the hashes of the table

        if further=='True':
            for i in self.table:
                self.table[i]['HASH'] = hashlib.sha256(self.table[i]['DATA']).hexdigest()
            return self.table
        else:
            return "hello"

