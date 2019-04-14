import asyncio, uvloop, argparse

from kademlia import network

parser = argparse.ArgumentParser()
parser.add_argument("listen", type=int)
parser.add_argument("handle", type=int)
args = parser.parse_args()

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

network = network.Network('127.0.0.1', args.listen, loop)
loop.run_until_complete(network.bootstrap())
loop.run_until_complete(network.listen(args.handle))