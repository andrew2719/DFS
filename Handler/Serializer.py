
# ```
# >>> str(x)
# "b'hello this is a string'"
# >>> str(x)[2:len(str(x))-1].encode()
# b'hello this is a string'
# ```
#
# ```
# >>> e
# bytearray(b'hello this is a string')
# >>> base64.b64encode(e)
# b'aGVsbG8gdGhpcyBpcyBhIHN0cmluZw=='
# >>> y = base64.b64encode(e).decode()
# >>> y
# 'aGVsbG8gdGhpcyBpcyBhIHN0cmluZw=='
# >>> base64.b64decode(y.encode())
# b'hello this is a string'
# ```

import base64

class b_64:
    # only for the binary data
    def __init__(self,data):
        self.data = data
    async def encode_data(self): # this gives the some MTI= kind of data, decode for taking that b'MTI=' to MTI=
        return base64.b64encode(self.data).decode()

    async def decode_data(self): # this gives the original binary data, encode for taking that MTI= to b'MTI='
        return base64.b64decode(self.data.encode())

class b_object:

    def __init__(self,data):
        self.data = data

    async def encode_data(self):
        return str(self.data).encode()

    async def decode_data(self):
        return eval(self.data.decode())

    async def stringify_encode_bin(self):
        return str(self.data)[2:len(str(self.data))-1].encode()
