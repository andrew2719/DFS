import asyncio
import tkinter as tk
from tkinter import filedialog
import os
import hashlib
import json
from client_logger import client_logger as c_logger
from FileManagement import chunker

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
                'sent_to': [],
            }
        '''
        self.hash_table = None #this is used to check the integrity of the file
        '''
        self.hash_table[i] = hashlib.sha256(chunk).hexdigest()
        '''

    async def append_data(self, data): # this will be completed when the read file is completed
        self.file_data += data
        self.file_data_copy += data
        self.hasher.update(data)
        self.file_size += len(data)

    async def connect_to_server(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        if self.reader and self.writer:
            c_logger.info('Connected to the server')

    async def write_(self, writer, data):
        writer.write(data)
        await writer.drain()

    async def meta_data(self, file_path):

        self.file_info = {
            "type" : "upload",
            "size": os.path.getsize(file_path),
        }

    async def read_file(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                await self.append_data(data)
                data = file.read(1024)

    async def prepare_data(self,file_path):
        await self.read_file(file_path) #this complete the data, hashing and size of the file
        await self.meta_data(file_path)
        self.look_up_table,self.hash_table = await chunker.Chunker(self.file_data).chunker()

    async def send_file(self, file_path):
        await self.prepare_data(file_path)

        # Send meta data
        await self.write_(self.writer, str(self.file_info).encode())
        # get the response for the meta data
        meta_data_response = await self.reader.read(1024)

        table = json.dumps(self.look_up_table).encode()
        #send the table to the serveras 1024 bytes at a time
        while table:
            await self.write_(self.writer, table)
            table = table[1024:]

        # get the response for the table (the hashes)
        response_hash_table = await self.reader.read(1024)
        response_hash_table = json.loads(response_hash_table.decode())

        # check if the hashes are same
        if response_hash_table == self.hash_table:
            c_logger.info("Hashes are same")
        else:
            c_logger.error("Hashes are not same")




    async def choose_file_and_send(self):
        await self.connect_to_server()

        # Open file explorer and get file path
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename()

        # Check if a file is selected
        if file_path:
            await self.send_file(file_path)

asyncio.run(Client().choose_file_and_send())
