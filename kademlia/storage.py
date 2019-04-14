import pickle

class Storage:
    def __init__(self):
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