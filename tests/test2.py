from kademlia import network
import uvloop, asyncio, hashlib

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

network1 = network.Network("127.0.0.1", 50001, [("127.0.0.1", 50000)])

loop.run_until_complete(network1.put("hello, world again"))
loop.run_until_complete(network1.get(hashlib.sha1("hello, world again".encode()).digest()))