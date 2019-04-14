import asyncio, uvloop, argparse

from kademlia import network

parser = argparse.ArgumentParser()
parser.add_argument("listen", type=int)
parser.add_argument("handle", type=int)
parser.add_argument("--bip", type=str)
parser.add_argument("--bport", type =int) 
args = parser.parse_args()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

network = network.Network('127.0.0.1', args.listen, loop)
if (args.bip, args.bport) == ("0", 0):
    loop.run_until_complete(network.bootstrap())
else:
    loop.run_until_complete(network.bootstrap([(args.bip, args.bport)]))
loop.run_until_complete(network.listen(args.handle))
loop.run_forever()