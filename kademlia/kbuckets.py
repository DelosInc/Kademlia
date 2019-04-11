import heapq, operator

class KBuckets:
    def __init__(self, node, k):
        self.node = node
        self.k = k
        self.buckets = [KBucket(0, 2 ** 160, self.k)]

    def add(self, node):
        index = self.find_bucket(node)
        if len(self.buckets[index].nodes) > self.k:
            self.split_bucket(index)
        self.buckets[index].add(node)

    def find_bucket(self, node):
        for index, bucket in enumerate(self.buckets):
            if node.num_id < bucket.upper:
                return index

    def find_neighbours(self, node, k = None):
        k = k or self.k
        nodes = []
        for neighbor in TableTraverser(self, node):
            if neighbor.id != node.id:
                heapq.heappush(nodes, (node.distance_to(neighbor), neighbor))
            if len(nodes) == k:
                break
        return list(map(operator.itemgetter(1), heapq.nsmallest(k, nodes)))

    def split_bucket(self, index):
        one, two = self.buckets[index].split()
        self.buckets[index] = one
        self.buckets.insert(index + 1, two)

class KBucket:
    def __init__(self, lower, upper, k):
        self.lower = lower
        self.upper = upper
        self.k = k
        self.nodes = {}

    def add(self, node):
        self.nodes[node.id] = node

    def get_nodes(self):
        return list(self.nodes.values())

    def in_range(self, node):
        return self.lower <= node.num_id <= self.upper

    def split(self):
        mid = (self.lower + self.upper) / 2
        one = KBucket(self.lower, mid, self.k)
        two = KBucket(mid + 1, self.upper, self.k)
        for node in self.get_nodes():
            bucket = one if node.long_id <= mid else two
            bucket.add(node)
        return (one, two)


class TableTraverser:
    def __init__(self, table, startNode):
        index = table.find_bucket(startNode)
        self.current_nodes = table.buckets[index].get_nodes()
        self.left_buckets = table.buckets[:index]
        self.right_buckets = table.buckets[(index + 1):]
        self.left = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_nodes:
            return self.current_nodes.pop()
        if self.left and self.left_buckets:
            self.current_nodes = self.left_buckets.pop().get_nodes()
            self.left = False
            return next(self)
        if self.right_buckets:
            self.current_nodes = self.right_buckets.pop(0).get_nodes()
            self.left = True
            return next(self)
        raise StopIteration
