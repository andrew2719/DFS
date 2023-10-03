
# converting binary to base64 and decoding it back to the base64
# what happens is that the binary data is converted to base64
# ex :
# >>> a = b'12'
# >>> import base64
# >>> b = base64.b64encode(a)
# >>> print(b)
# b'MTI='
# >>> b.decode()
# 'MTI='

# so again if we want to get the original binary data we need to convert encode and then decode with base64
# >>> b
# 'MTI='
# >>> base64.b64decode(b.encode())
# b'12'
# any type of data can be encoded and decoded with base64
import base64

async def encode_data(data): # this gives the some MTI= kind of data, decode for taking that b'MTI=' to MTI=
    return base64.b64encode(data).decode()

async def decode_data(data): # this gives the original binary data, encode for taking that MTI= to b'MTI='
    return base64.b64decode(data.encode())