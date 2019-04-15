import pickle
from kademlia.kbuckets import KBuckets

class Node:
    def __init__(self, id, ip = None, port = None):
        self.id = id
        self.num_id = int(id, 16)
        self.ip = ip
        self.port = port

    def distance(self, node):
        return self.num_id ^ node.num_id

    def same(self, node):
        return self.ip == node.ip and self.port == node.port

    def serialized(self):
        return (self.id, self.ip, self.port)