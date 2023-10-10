class ReadWrite:

    def __init__(self,reader,writer):
        self.reader = reader
        self.writer = writer
    async def read_loop(self):
        buffer = b""
        delimiter = b"@@EOM@@"

        while True:
            chunk = await self.reader.read(1024)
            buffer += chunk

            # Check if the delimiter is in the buffer
            delim_index = buffer.find(delimiter)
            if delim_index != -1:
                message = buffer[:delim_index]  # Extract the complete message
                buffer = buffer[delim_index + len(delimiter):]  # Remainder begins the next message
                return message

    async def write_(self, data):
        self.writer.write(data)
        await self.writer.drain()

    async def write_in_loop(self,data):
        delimiter = b"@@EOM@@"
        data_with_delimiter = data + delimiter
        table_len = len(data_with_delimiter)

        buffer = data_with_delimiter
        chunk_size = 1024

        while buffer:
            chunk = buffer[:chunk_size]
            buffer = buffer[chunk_size:]

            await self.write_(chunk)


