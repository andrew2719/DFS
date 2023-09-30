import asyncio
import aiofiles
import os
import json
from DFS_main.logger import logger
import JsonHandler
from settings import FREE_SPACE



class Handle:
    def __init__(self, reader, writer, request):
        self.reader = reader
        self.writer = writer
        self.request = request
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
            return await self.HandleUpload()

        elif self.request["type"] == "download":
            pass


    async def HandleUpload(self):
        pass



