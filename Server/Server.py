import asyncio
import aiofiles
import os
import json
import sys
from DFS_main.logger import logger
import settings
from Handler import Handler
from Handler import SelfHandler
from Handler import PeerHandler
from Handler import Responses


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
            data = await self_handler.read_look_up_table()

            logger.info("starting the distribution of data")
            if data:

                final_table,sent_status = await PeerHandler.DataDistributor(self.peer_connections).distribute(data)
                if sent_status:
                    logger.info("Data sent successfully")
                    logger.info("Final table is : " + str(final_table))
                else:
                    logger.info("Data not sent successfully")
            else:
                logger.info("Data not sent successfully")




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

            handle = await handler.Handler()

            # writer.write(handle)
            #
            # await writer.drain()

            await Responses.ReadWrite(reader,writer).write_in_loop(handle.encode())



    async def start_server(self):
        server = await asyncio.start_server(self.handle_inbound, '0.0.0.0', self.port)
        logger.info('Started server on port {}'.format(self.port))

        # Connect to all known peers
        logger.info("Started connecting to peers")
        for peer in self.peers:
            asyncio.create_task(self.connect_to_peer(peer))

        await server.serve_forever()

    # async def connect_to_peer(self, peer_ip, port=8888):
    #     try:
    #         reader, writer = await asyncio.open_connection(peer_ip, port)
    #         self.peer_connections[peer_ip] = (reader, writer)
    #         logger.info(f"Node {self.port} connected to peer {peer_ip}:{port}")
    #
    #     except Exception as e:
    #         logger.error(f"Error connecting to {peer_ip}:{port}. Error: {e}")
    async def connect_to_peer(self, peer_ip, port=8888):
        attempt = 0
        max_retries = 2
        backoff_initial_delay = 1
        backoff_factor = 2
        max_backoff = 60

        while attempt < max_retries:
            try:
                reader, writer = await asyncio.open_connection(peer_ip, port)
                self.peer_connections[peer_ip] = (reader, writer)
                initial = await reader.read(1024)
                initial = initial.decode()
                logger.info(initial)

                logger.info(f"Node {self.port} connected to peer {peer_ip}:{port}")
                return  # Exit the function after a successful connection
            except Exception as e:
                attempt += 1
                logger.error(f"Attempt {attempt}: Error connecting to {peer_ip}:{port}. Error: {e}")
                if attempt >= max_retries:
                    logger.error(f"Max retries reached. Unable to connect to {peer_ip}:{port}.")
                    break  # Exit the loop after max retries
                backoff_delay = min(max_backoff, backoff_initial_delay * (backoff_factor ** attempt))
                logger.info(f"Retrying in {backoff_delay} seconds...")
                await asyncio.sleep(backoff_delay)

async def main():
    # Node initialized with peers (replace with your IPs)
    node = Server(8888, ['10.10.13.255'])
    await node.start_server()