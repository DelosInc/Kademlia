import pickle
from kademlia.kbuckets import KBuckets

class Node:
    def __init__(self, id, ip, port, k):
        self.id = id
        self.num_id = int(id.hex(), 16)
        self.ip = ip
        self.port = port
        self.kbuckets = KBuckets(self, k)       #TODO: decide on movement to separate class
        try:
            with open("storage.pickle", 'rb') as storage:
                self.storage = pickle.load(storage)
        except IOError:
            self.storage = {}

    def stop(self):
        with open("storage.pickle", 'wb') as storage:
            pickle.dump(self.storage, storage)

    def store(self, key, value):
        self.storage[key] = value

    def retrieve(self, key):
        if self.storage.get(key) is not None:
            return self.storage.get(key)
        return None

    def distance(self, node):
        return self.num_id ^ node.num_id

    def same(self, node):
        return self.ip == node.ip and self.port == node.port
