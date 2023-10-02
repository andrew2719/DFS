import hashlib


class FileObject:

    def __init__(self,file_size):
        self.file_hash = hashlib.sha256()
        self.file_data = bytearray()
        self.file_size = file_size
        self.sent_from = None
        self.storage_path = None

    async def add_data(self, data):
        self.file_data += data
        self.file_hash.update(data)
