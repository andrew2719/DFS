import hashlib
from settings import RECEIVED_FILES

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

    async def save_file(self):
        # save to the system in the received_files folder that is from the RECEIVED_FILES
        with open(RECEIVED_FILES + self.file_hash.hexdigest(), 'wb') as file:
            file.write(self.file_data)
            file.close()

    async def save_(self):

        try:
            await self.save_file()
            return True

        except Exception as e:
            return e
