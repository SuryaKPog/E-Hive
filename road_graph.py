import heapq
import math

class RoadGraph:
    def __init__(self):
        self.graph = {}

    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, a, b):
        # undirected road
        dist = math.hypot(a[0] - b[0], a[1] - b[1])
        self.graph[a].append((b, dist))
        self.graph[b].append((a, dist))

    def shortest_path_distance(self, start, end):
        # Dijkstra
        pq = [(0, start)]
        visited = set()

        while pq:
            cost, node = heapq.heappop(pq)

            if node == end:
                return cost

            if node in visited:
                continue

            visited.add(node)

            for neighbor, weight in self.graph[node]:
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor))

        return float("inf")
