import hashlib, random, asyncio, heapq, pickle
from aiorpc import register, serve, RPCClient

from kademlia.node import Node
from kademlia.kbuckets import KBuckets
from kademlia.storage import Storage

class Network:
    def __init__(self, ip, port, loop, k = 20, alpha = 3, id = None):
        self.k = k
        self.alpha = alpha
        self.ip = ip
        self.port = port
        self.loop = loop
        self.node = Node(hashlib.sha1(str(random.getrandbits(255)).encode('utf8')).digest(), ip, port, k)
        self.kbuckets = KBuckets(self, k)
        self.storage = Storage()

    async def listen(self, port):
        register("ping", self.ping)
        register("find_value", self.find_value)
        register("find_node", self.find_node)
        register("store", self.store)
        asyncio.ensure_future(asyncio.start_server(serve, self.ip, self.port, loop=self.loop))
        asyncio.ensure_future(asyncio.start_server(self.handle, self.ip, port, loop=self.loop))

    async def handle(self, reader, writer):
        data = pickle.loads(await reader.read())
        data = await getattr(self, data["func"])(data["args"])
        writer.write(pickle.dumps(data))
        await writer.drain()

    async def bootstrap(self, addrs = None):
        if addrs is not None:
            node_ids = await asyncio.gather(*[await self.client(addr, self.ping) for addr in addrs])
            nodes = [Node(id, addr[0], addr[1], self.k) for id, addr in zip(node_ids, addrs) if id is not None]
            return await asyncio.gather(*[await self.client((node.ip, node.port), self.find, self.find_node, self.node) for node in nodes])

    async def client(self, addr, func, *args):
        client = RPCClient(addr[0], addr[1])
        args = (self.node.serialized(), *args)
        print(args)
        return self.loop.run_until_complete(await client.call(func.__name__, *args), loop = self.loop)

    async def ping(self, node):
        self.kbuckets.add(Node(node[0], node[1], node[2]))
        print("pinged")
        return self.node.id

    async def find_node(self, node, node_to_search):
        self.kbuckets.add(Node(node[0], node[1], node[2]))
        return self.kbuckets.find_neighbours(node_to_search, self.k)

    async def find_value(self, node, key):
        self.kbuckets.add(Node(node[0], node[1], node[2]))
        for node in self.kbuckets.find_neighbours(node, self.k):
            if self.storage.retrieve(key):
                return self.storage.retrieve(key)
        return self.kbuckets.find_neighbours(node, self.k)

    async def store(self, node, key, value):
        self.kbuckets.add(Node(node[0], node[1], node[2]))
        self.storage.store(key, value)
        return True

    async def find(self, node, func, *args):
        while True:
            closest = None
            shortlist =  []
            contacts = []
            for node in self.kbuckets.find_neighbours(self.node, self.alpha):
                heapq.heappush(shortlist, (node.distance_to(self.node), node))
            shortlist.append(await asyncio.gather(*[await self.client((node.ip, node.port), func, *args) for node in heapq.nsmallest(self.alpha, shortlist)]))
            if closest == heapq.nsmallest(1, shortlist) or len(contacts) == self.k:
                break
            else:
                contacts.append(closest)
                closest = heapq.nsmallest(1, shortlist)

    async def ping_handler(self, ip, port):
        self.client((ip, port), self.ping, self.node)

    async def get(self, key):
        value = self.storage.retrieve(key)
        if value is None:
            node_to_get = Node(key, k = self.k)
            nearest = self.kbuckets.find_neighbours(node_to_get, self.alpha)
            results = await asyncio.gather(*[await self.client((node.ip, node.port), self.find, self.find_value, key) for node in nearest])
            values = list(filter(lambda x: isinstance(x, str), results))
            if values:
                return values[0]
            else:
                return None
        return value

    async def put(self, value):
        key = hashlib.sha1(value.encode()).digest()
        node_to_put = Node(key, k = self.k)
        nearest = self.kbuckets.find_neighbours(node_to_put, self.alpha)
        return await asyncio.gather(*[await self.client((node.ip, node.port), self.find, self.store, key, value) for node in nearest])
