import asyncio, pickle, argparse

async def to_daemon(port, data):
    reader, writer = await asyncio.open_connection('127.0.0.1', port)
    writer.write(pickle.dumps(data))
    data = await reader.read()
    print(data)
    return pickle.loads(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    args = parser.parse_args()
    while True:
        data = {"func": input(), "args": input()}
        print(data)
        asyncio.run(to_daemon(args.port, data))

if __name__ == "__main__":
    main()