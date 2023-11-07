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

        self.data = b''
        self.chunk_size = 1024
        self.hash_table = {}
        self.read_in_loop, self.write_ = (Responses.ReadWrite(self.reader, self.writer).read_in_loop,
                                          Responses.ReadWrite(self.reader, self.writer).write_)
        self.write_in_loop = Responses.ReadWrite(self.reader,self.writer).write_in_loop


    async def read_look_up_table(self):

        logger.info("reading the table")

        self.data = await self.read_in_loop()

        # logger.info(self.table)
        logger.info("table read, length of the table is : " + str(len(self.data)))

        self.hash = hashlib.sha256(self.data).hexdigest()

        await self.write_in_loop(self.hash.encode())

        further = await self.read_in_loop()

        further = further.decode()

        logger.info(further)

        if further == 'True':
            pass
        else:
            return False

