import hashlib, random, asyncio, uvloop, heapq
from aiorpc import register, serve, RPCClient

from kademlia.node import Node

class Network:
    def __init__(self, ip, port, nodes, k = 20, alpha = 3, id = None):
        self.k = k
        self.alpha = alpha
        self.node = Node(hashlib.sha1(str(random.getrandbits(255)).encode('utf8')).digest(), ip, port, k)
        loop = uvloop.new_event_loop()                          #TODO: decide movement to userspace
        asyncio.set_event_loop(loop)
        self.server = self.server_init(loop)
        loop.run_until_complete(self.bootstrap(nodes))
        loop.run_forever()

    def server_init(self, loop):
        register("ping", self.ping)
        register("find_value", self.find_value)
        register("find_node", self.find_node)
        register("store", self.store)
        return asyncio.start_server(serve, '127.0.0.1', 60000, loop=loop)

    async def client(self, addr, func, *args):
        async with RPCClient(addr[0], addr[1]) as client:       #TODO: test and fix problem with context managed RPCClient
            ret = await client.call(func.func_name, self.node, *args)
        return ret

    async def bootstrap(self, addrs = None):
        node_ids = await asyncio.gather(*list(map(lambda addr: await self.client(addr, self.ping, self.node), addrs)))
        nodes = [Node(id, ip, port, self.k) for id, (ip, port) in zip(node_ids, addrs) if id is not None]
        return await asyncio.gather(*list(map(lambda node: await self.client((node.ip, node.port), self.find, self.find_node, self.node), nodes)))

    async def ping(self, node):
        self.node.kbuckets.add(node)
        return self.node.id

    async def find_node(self, node, node_to_search):
        self.node.kbuckets.add(node)
        return node.kbuckets.find_neighbours(node_to_search, self.k)

    async def find_value(self, node, key):
        self.node.kbuckets.add(node)
        for node in node.kbuckets.find_neighbours(node, self.k):
            if node[key]:
                return node[key]
        return node.kbuckets.find_neighbours(node, self.k)

    async def store(self, node, key, value):
        self.node.kbuckets.add(node)
        self.node.store(key, value)
        return True

    async def find(self, node, func, *args):
        while True:
            closest = None
            shortlist =  []
            contacts = []
            for node in self.node.kbuckets.find_neighbours(self.node, self.alpha):
                heapq.heappush(shortlist, (node.distance_to(self.node), node))
            shortlist.append(await asyncio.gather(*[getattr(self, func)(node, *args) for node in heapq.nsmallest(self.alpha, shortlist)]))
            if closest == heapq.nsmallest(1, shortlist) or len(contacts) == self.k:
                break
            else:
                contacts.append(closest)
                closest = heapq.nsmallest(1, shortlist)

    async def get(self, key):
        value = self.node.retrieve(key)
        if value is None:
            node_to_get = Node(key, k = self.k)
            nearest = self.node.kbuckets.find_neighbours(node_to_get, self.alpha)
            results = await asyncio.gather(*list(map(lambda node: await self.client((node.ip, node.port), self.find, self.find_value, key), nearest)))
            values = list(filter(lambda x: isinstance(x, str), results))
            if values:
                return values[0]
            else:
                return None
        return value

    async def put(self, value):
        key = hashlib.sha1(value).digest()
        node_to_put = Node(key, k = self.k)
        nearest = self.node.kbuckets.find_neighbours(node_to_put, self.alpha)
        return await asyncio.gather(*list(map(lambda node: await self.client((node.ip, node.port), self.find, self.store, key, value), nearest)))
