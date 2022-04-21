#coding utf-8
import vb
from struct import pack
f = open('/Users/ryan_kim/Documents/programming/enterprise-service-technique/06/eid_tags.txt', 'r')
outFile = open('eid_tags_encode.bin', 'ab')
for line in f:
    title, content = line.split("\t")
    params = [x for x in content.split(",")]
    vb_vals = []
    params_len = 0
    sum_params = 0
    for p in params:
        p = int(p)
        p -= sum_params
        sum_params += p
        val = vb.encode_number(p)
        params_len += len(val)
        vb_vals.append(val)
        row = "{}{}{}".format(pack('2i', len(title), params_len), title, b''.join(vb_vals))
        outFile.write(bytes(row, encoding="utf8"))

f.close()
outFile.close()
