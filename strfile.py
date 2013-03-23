import random
import struct

class Strfile(object):
    HEADER_LEN = 24
    
    def __init__(self, data_fh, idx_fh=None):    
        if idx_fh is None:
            idx_fh = data_fh + ".dat"
        if isinstance(data_fh, basestring):
            data_fh = open(data_fh, 'r')
        self.data_fh = data_fh
        if isinstance(idx_fh, basestring):
            idx_fh = open(idx_fh, 'r')
        self.idx_fh = idx_fh
        self.version, self.numstr, self.longlen, self.shortlen, self.flags, \
          self.delim = struct.unpack('!LLLLLc', idx_fh.read(self.HEADER_LEN - 3))
    
    def read(self, num):
        self.idx_fh.seek(self.HEADER_LEN + 4 * num)
        offset = struct.unpack('!L', self.idx_fh.read(4))[0]
        self.data_fh.seek(offset)
        ret = []
        while True:
            line = self.data_fh.readline()
            if self.flags & 0x4:
                line = line.decode('rot13')
            if line.strip() == self.delim or line == '':
                return ret
            ret.append(line)

    def read_random(self):
        return self.read(random.randrange(self.numstr))
