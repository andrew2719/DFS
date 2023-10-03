import asyncio
import aiofiles
import os
import json
from DFS_main.logger import logger
from . import JsonHandler
from settings import FREE_SPACE
from FileManagement import FileObjector


class Handle:
    # this class is used to handle the request from the other nodes
    # it just stores the data to the system (only a single piece of some data is sent from other node(inbound) for storing purposes)
    def __init__(self, reader, writer, request):
        self.reader = reader
        self.writer = writer
        self.request = request
        self.file_object = None
        '''
        request  = {
            "type" : "upload/download",
            "hash" : "hash of the file(it is the name for identification)",
            "size" : "size of the file(in bytes)",
        }
        '''

    async def conversion(self):
        self.request = await JsonHandler.convert_json_to_dict(self.request)

    async def acknowledgment(self, bool,extras = None):

        response = {
            'status':bool,
            'extras':extras
        }

        return JsonHandler.convert_dict_to_json(response)
    async def Handler(self):
        await self.conversion()
        logger.info("Handling , request is : " + self.request)

        # check for the storage for saving the file in the system
        size = self.request["size"]
        if size > FREE_SPACE:
            logger.error("Not enough space in the system")
            return self.acknowledgment(False)

        if self.request["type"] == "upload":
            self.file_object = FileObjector.FileObject(size)
            return await self.HandleUpload()

        elif self.request["type"] == "download":
            pass


    async def HandleUpload(self):
        size = 0
        # reading the file 1024 bytes at a time
        while size < self.request["size"]:
            data = await self.reader.read(1024)
            size += len(data)
            self.file_object.add_data(data)

        #send the hash to the client

        hash = self.file_object.file_hash.hexdigest() #string of hash


