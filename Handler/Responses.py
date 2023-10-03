class ReadWrite:

    def __init__(self,reader,writer):
        self.reader = reader
        self.writer = writer
    async def read_(self):
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
