import asyncio
import uvloop
import rpyc

from aiorpc import register, serve

def listen():
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    register("ping", ping)
    register("find_value", find_value)
    register("find_node", find_node)
    register("store", store)
    coro = asyncio.start_server(serve, '127.0.0.1', 50000, loop=loop)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())

async def ping(id, ip, port):
    return id

async def find_node(id):
    pass

async def find_value(key):
    pass

async def store(key, value):
    pass