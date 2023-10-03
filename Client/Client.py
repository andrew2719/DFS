import asyncio
import tkinter as tk
from tkinter import filedialog
import os
import hashlib
import json
from .client_logger import client_logger as c_logger
from FileManagement import chunker
import base64
from Handler import Responses




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
        self.read_ = Responses.ReadWrite(self.reader, self.writer).read_
        self.write_ = Responses.ReadWrite(self.reader, self.writer).write_
        response = await self.reader.read(1024)
        c_logger.info(response.decode())
        if self.reader and self.writer:
            c_logger.info('Connected to the server')

    # async def write_(self, writer, data):
    #     writer.write(data)
    #     await writer.drain()

    async def meta_data(self, file_path):

        self.file_info = {
            'NODE':'SELF',
            "TYPE" : "UPLOAD",
            "SIZE": os.path.getsize(file_path),
        }

    async def read_file(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                await self.append_data(data)
                data = file.read(1024)

    async def prepare_data(self,file_path):

        c_logger.info('reading file...')
        await self.read_file(file_path) #this complete the data, hashing and size of the file
        c_logger.info('file read')

        c_logger.info('preparing meta data...')
        await self.meta_data(file_path)
        c_logger.info('meta data prepared')

        c_logger.info('preparing look up table...')
        try:
            self.look_up_table,self.hash_table = await chunker.Chunker(self.file_data).chunker() # dicts
            # c_logger.info(self.look_up_table)
            c_logger.info(self.hash_table)
            c_logger.info('look up table prepared, ',type(self.look_up_table))
        except Exception as e:
            c_logger.error(e)

    async def send_file(self, file_path):

        c_logger.info('preparing data...')
        await self.prepare_data(file_path)
        c_logger.info('data prepared')

        # Send meta data
        await self.write_(json.dumps(self.file_info).encode())
        meta_data_response = await self.reader.read(1024)
        c_logger.info(f'meta data response: {meta_data_response.decode()}')
        # serialize the look up table

        # seralise the look up table to tble using the base64 if any binary data is present
        table  = {}
        for i in self.look_up_table:
            table[i] = {}
            for j in self.look_up_table[i]:
                if j == "DATA":
                    table[i][j] = base64.b64encode(self.look_up_table[i][j]).decode()
                else:
                    table[i][j] = self.look_up_table[i][j]

        table = json.dumps(table).encode()
        # add @@EOM@@ to the end of the table
        table += b"@@EOM@@"
        table_len = len(table)

        # send the table to the serveras 1024 bytes at a time
        # for i in range(0,table_len,1024):
        #     c_logger.info(f'sending {i} to {i+1024}')
        #     await self.write_(table[i:i+1024])
        #     if (i+1024 >= table_len) or (not table[i+1024:]):
        #         break
        total_bytes_sent = 0

        # for i in range(0, table_len, 1024):
        #     start_idx = i
        #     end_idx = min(i + 1024, table_len)
        #     chunk_size = end_idx - start_idx
        #
        #     await self.write_(table[start_idx:end_idx])
        #
        #     total_bytes_sent += chunk_size
        #     c_logger.info(
        #         f'Sending bytes {start_idx} to {end_idx}. Chunk size: {chunk_size}. Total bytes sent: {total_bytes_sent}')
        #
        #     if end_idx >= table_len or not table[end_idx:]:
        #         break

        delimiter = b"@@EOM@@"
        table_with_delimiter = table + delimiter
        table_len = len(table_with_delimiter)

        buffer = table_with_delimiter
        chunk_size = 1024

        while buffer:
            chunk = buffer[:chunk_size]
            buffer = buffer[chunk_size:]

            await self.write_(chunk)

            c_logger.info(f'Sent chunk of size: {len(chunk)}. Remaining data length: {len(buffer)}')

        c_logger.info('table sent')
        # await self.write_(self.writer, "@@EOM@@")




        c_logger.info('waiting for response hash table')

        response_hash_table = await self.read_()

        response_hash_table = json.loads(response_hash_table.decode())
        c_logger.info(response_hash_table)
        c_logger.info('response hash table received')

        self.hash_table = json.dumps(self.hash_table).encode()
        self.hash_table = json.loads(self.hash_table.decode())

        if response_hash_table == self.hash_table:
            c_logger.info("Hashes are same")
            await self.write_("True".encode())
        else:
            await self.write_("False".encode())
            c_logger.error("Hashes are not same")


    async def choose_file_and_send(self):
        await self.connect_to_server()

        # Open file explorer and get file path
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename()

        # Check if a file is selected
        if file_path:
            c_logger.info(f'File selected: {file_path}')
            await self.send_file(file_path)

asyncio.run(Client().choose_file_and_send())
