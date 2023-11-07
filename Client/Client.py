import asyncio
import tkinter as tk
from tkinter import filedialog
import os
import hashlib
import json
from .client_logger import client_logger as c_logger
from FileManagement import chunker
import base64
from Handler import Responses, Serializer



class Client:
    def __init__(self):
        self.file_data = bytearray() # this is byte array of the file nothing but the binary data of the file
        self.file_data_copy = bytearray()
        self.hasher = hashlib.sha256()
        self.file_size = 0
        self.file_info = None
        self.look_up_table = None # this will be sent to the server
        '''
        self.look_up_table[i] = {
                'INDEX': i,
                'DATA': chunk,
                'HASH': None,
                'SIZE': len(chunk),
            }
        '''
        self.hash_table = None
        '''
        self.hash_table[i] = hashlib.sha256(chunk).hexdigest()
        '''

    async def append_data(self, data): # this will be completed when the read file is completed
        self.file_data += data
        self.file_data_copy += data
        self.hasher.update(data)
        self.file_size += len(data)

    async def connectToServer(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)

        if self.reader and self.writer:
            c_logger.info('Connected to the server')

        read_write_obj = Responses.ReadWrite(self.reader, self.writer)
        self.read_in_loop = read_write_obj.read_in_loop
        self.write_ = read_write_obj.write_
        self.write_in_loop = read_write_obj.write_in_loop

        response = await self.reader.read(1024)
        c_logger.info(response.decode())

    async def metaData(self, size,file_path):
        extension_of_file = os.path.splitext(file_path)[1]
        self.file_info = {
            'NODE':'SELF',
            "TYPE" : "UPLOAD",
            "SIZE": size,
            "EXTENSION": extension_of_file,
        }

    async def readFile(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                await self.append_data(data)
                data = file.read(1024)
    async def serializeTable(self):
        table = {}
        for i in self.look_up_table:
            table[i] = {}
            for j in self.look_up_table[i]:
                if j == "DATA":
                    table[i][j] = base64.b64encode(self.look_up_table[i][j]).decode()
                else:
                    table[i][j] = self.look_up_table[i][j]

        self.table = json.dumps(table).encode()
        return self.table

    async def prepare_data(self,file_path):

        c_logger.info('reading file...')
        await self.readFile(file_path) #this complete the data, hashing and size of the file
        c_logger.info('file read')
        self.hash = self.hasher.hexdigest()

        size = len(self.file_data)
        c_logger.info('preparing meta data...')
        await self.metaData(size,file_path)
        c_logger.info('meta data prepared')



    async def SendFile(self, file_path):

        c_logger.info('preparing data...')
        await self.prepare_data(file_path)
        c_logger.info('data prepared')

        await self.write_(json.dumps(self.file_info).encode())
        meta_data_response = await self.reader.read(1024)
        c_logger.info(f'meta data response: {meta_data_response.decode()}')

        c_logger.info('sending data...')
        await self.write_in_loop(self.file_data)
        c_logger.info('data sent')

        c_logger.info('waiting for response hash')
        response_hash = await self.read_in_loop()

        response_hash = response_hash.decode()
        c_logger.info(response_hash)
        c_logger.info('response hash received')

        if response_hash == self.hash:
            c_logger.info("Hashes are same")
            await self.write_in_loop("True".encode())
        else:
            await self.write_in_loop("False".encode())
            c_logger.error("Hashes are not same")

        # final_response = await self.read_in_loop()

    async def chooseFileAndSend(self):
        await self.connectToServer()

        # Open file explorer and get file path
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename()

        # Check if a file is selected
        if file_path:
            c_logger.info(f'File selected: {file_path}')
            await self.SendFile(file_path)

#         close the self.writer
        self.writer.close()

asyncio.run(Client().chooseFileAndSend())
