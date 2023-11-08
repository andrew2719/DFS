import asyncio
import aiofiles
import os
import json
from DFS_main.logger import logger
from . import JsonHandler
from settings import FREE_SPACE
from FileManagement import FileObjector
from . import Responses
import hashlib
import json


class Handle:
    # this class is used to handle the request from the other nodes
    # it just stores the data to the system (only a single piece of some data is sent from other node(inbound) for storing purposes)
    def __init__(self, reader, writer, request):
        self.reader = reader
        self.writer = writer
        self.request = request
        self.file_object = None
        self.read_write_obj = Responses.ReadWrite(self.reader,self.writer)
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

            # ack = await self.acknowledgment(False,"Not enough space in the system")
            # await self.read_write_obj.write_in_loop(ack.encode())
            response = {
                'status':False,
                'extras':"Not enough space in the system"
            }
            await self.read_write_obj.write_in_loop(json.dumps(response).encode())

        if self.request["type"] == "upload":
            self.file_object = FileObjector.FileObject(size)

            response = {
                'status':True,
                'extras':None
            }
            await self.read_write_obj.write_in_loop(json.dumps(response).encode())
            return await self.HandleUpload()

        elif self.request["type"] == "download":
            pass


    async def HandleUpload(self):
        size = 0
        # reading the file 1024 bytes at a time
        data = await self.read_write_obj.read_in_loop()

        hash = hashlib.sha256(data).hexdigest()
        logger.info("Hash of the file is : " + hash)
        await self.read_write_obj.write_in_loop(hash.encode())

        # further = await Responses.ReadWrite(self.reader,self.writer).read_in_loop()
        further = await self.read_write_obj.read_in_loop()

        further = further.decode()

        logger.info(further)

        if further == 'True':
            # saving the data to the system
            self.file_object.file_data = data
            self.file_object.hash = hash
            self.file_object.size = len(data)
            self.file_object.name = hash
            self.file_object.sent_from = self.writer.get_extra_info('peername')

            try:
                save_status = await self.file_object.save_()
                if save_status:
                    logger.info("File saved successfully")
                    return await self.acknowledgment(True)
                else:
                    logger.error(save_status)
                    return await self.acknowledgment(False)
            except Exception as e:
                logger.error(e)
                return await self.acknowledgment(False)



