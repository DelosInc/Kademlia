# Kademlia

Python implementation of the Kademlia DHT using [asyncio](https://docs.python.org/3/library/asyncio.html).

# Source

[Kademlia: A Peer-to-peer Information System Based on the XOR Metric](http://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf)

# Developement Notes

The project is developed in Python 3.7, packaged using Pipenv and depends on [aiorpc](https://github.com/choleraehyq/aiorpc).
Due to the changing nature of the asyncio spec, compatibility with past versions <3.5 is not guaranteed.

```
git clone https://github.com/DelosInc/kademlia.git
cd kademlia
pipenv install --deploy
pipenv shell
```

# License

The project is licensed under GPL 3.0
