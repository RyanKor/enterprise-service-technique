#coding utf-8
import vb
from struct import unpack

f = open('eid_tags_encode.bin', 'rb')
while True:
    byte = f.read(8)
    if not byte:
        break
        title_len, params_len = unpack('2i', byte)
        title = f.read(title_len)
        params = []
        print(title)
        for p in vb.decode(f.read(params_len)):
            print(p)

f.close()
