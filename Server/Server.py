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
        # writer.write(f"you are connected to {self.port}".encode())
        # await writer.drain()

        request = await reader.read(1024) # the type of request , size of the file, the name of the file, later after making required arrangements the ccontent of the file is sent from the client
        request = json.loads(request.decode())

        if request["NODE"] == "SELF":

            logger.info(f'request from the client {request}')

            ask = {"status":True,"request":request}
            await self.write_(writer,json.dumps(request).encode())
            self_handler = SelfHandler.SelfHandle(reader,writer,request,self.peer_connections)
            read_look_up = await self_handler.read_look_up_table()

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