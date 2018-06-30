import fileinput
import sys
from time import time
from enum import Enum

from onion.frontend import Client


class PusherMode(Enum):
    Simple = "simple"
    LargeJson = "json"


class PusherCompress(Enum):
    NoCompress = "none"
    BZip2 = "bzip2"
    GZip = "gzip"


class Pusher():
    def __init__(self, frontend_address: str, mode: PusherMode=PusherMode.Simple):
        self.client: Client = Client(frontend_address)
        self.mode: PusherMode = mode
        pass

    def push(self, filepath: str = "-", compress: PusherCompress = PusherCompress.NoCompress):
        push_function = self._push_json if self.mode == PusherMode.LargeJson else self._push_simple

        self.client.connect()
        
        file = self.open(filepath, compress)
        
        for line in file:
            push_function(line)

        self.client.disconnect()
    
    def open(self, file, compress, encoding='utf-8'):
        if file == "-":
            file = sys.stdin.buffer

        if compress == PusherCompress.GZip:
            import gzip
            return gzip.open(file, 'rt', encoding=encoding)
        elif compress == PusherCompress.BZip2:
            import bz2
            return bz2.open(file, 'rt', encoding=encoding)
        else:
            if file == sys.stdin:
                return file
            return open(file, 'rt', encoding=encoding)

    def _push_json(self, line: str):
        if not line or line[0] == "[" or line[0] == "]":
            return

        if line[-2] == ",":
            self.client.send(line[:-2])
        else:
            self.client.send(line[:-1])

    def _push_simple(self, line: str):
        if line and line[-1] == '\n':
            line = line[:-1]
        self.client.send(line)
