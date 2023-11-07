import asyncio
import aiofiles
import os
import json
import sys
from DFS_main.logger import logger
import settings
from Handler import Handler
from Handler import SelfHandler


class Server:
    def __init__(self, port, peers=[], save_path=settings.RECEIVED_FILES):
        self.port = port
        self.peers = peers
        self.peer_connections = {}  # To store connection objects for peers
        self.save_path = save_path

        if not os.path.exists(save_path):
            os.makedirs(save_path)

    async def write_(self,writer,data):
        writer.write(data)
        await writer.drain()


    async def handle_inbound(self, reader, writer):
        addr = writer.get_extra_info('peername')[0]
        logger.info(f"Node {self.port} received connection from {addr}")
        await self.write_(writer,f"you are connected to {self.port}".encode())

        request = await reader.read(1024)
        request = json.loads(request.decode())

        if request["NODE"] == "SELF":
            ask = {"status":True,"request":request}
            logger.info(ask)

            await self.write_(writer,json.dumps(request).encode())

            self_handler = SelfHandler.SelfHandle(reader,writer,request,self.peer_connections)
            read_look_up,hash_table = await self_handler.read_look_up_table()
            # logger.info("read look up table is : " + str(read_look_up))
            # logger.info("hash table is : " + str(hash_table))


            # sorted_keys = sorted(read_look_up.keys())
            # original_data = b"".join([read_look_up[i]['DATA'] for i in sorted_keys])
            # # add the extension from request['EXTENSION'] and save to save_path as file_1
            # file_name = os.path.join(self.save_path, f"file_1{request['EXTENSION']}")
            # async with aiofiles.open(file_name, 'wb') as file:
            #     await file.write(original_data)
            #     logger.info(f"File {file_name} saved successfully")


            logger.info("closing the connection with the node : " + str(addr))
            writer.close()


        else:

            handler = Handler.Handle(reader,writer,request)

            handle = await handler.Handler() # sends back true or false stating the success

            writer.write(handle)

            await writer.drain()


    async def start_server(self):
        server = await asyncio.start_server(self.handle_inbound, '0.0.0.0', self.port)
        logger.info('Started server on port {}'.format(self.port))

        # Connect to all known peers
        logger.info("Started connecting to peers")
        for peer in self.peers:
            asyncio.create_task(self.connect_to_peer(peer))

        await server.serve_forever()

    async def connect_to_peer(self, peer_ip, port=8888):
        try:
            reader, writer = await asyncio.open_connection(peer_ip, port)
            self.peer_connections[peer_ip] = (reader, writer)
            logger.info(f"Node {self.port} connected to peer {peer_ip}:{port}")

        except Exception as e:
            logger.error(f"Error connecting to {peer_ip}:{port}. Error: {e}")

async def main():
    # Node initialized with peers (replace with your IPs)
    node = Server(8888, ['10.10.2.113'])
    await node.start_server()