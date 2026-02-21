from road_graph import RoadGraph
import math

# =========================
# ROAD GRAPH INITIALIZATION
# =========================
ROAD_GRAPH = RoadGraph()

# =========================
# CITY-LIKE ROAD NETWORK
# =========================

ROAD_NODES = []

# -------------------------
# Horizontal roads (3 main streets)
# -------------------------
for y in [0, 4, 8]:
    for x in range(0, 13, 2):
        ROAD_NODES.append((x, y))

# -------------------------
# Vertical connectors (avenues)
# -------------------------
for x in [4, 8]:
    for y in range(0, 9, 2):
        ROAD_NODES.append((x, y))

# -------------------------
# Curved arterial road (right side)
# -------------------------
CURVE = [
    (10, 2), (11, 3), (12, 4), (11, 5), (10, 6)
]
ROAD_NODES.extend(CURVE)

# -------------------------
# Add nodes to graph
# -------------------------
for n in ROAD_NODES:
    ROAD_GRAPH.add_node(n)

# -------------------------
# Horizontal connections
# -------------------------
for y in [0, 4, 8]:
    for x in range(0, 11, 2):
        ROAD_GRAPH.add_edge((x, y), (x + 2, y))

# -------------------------
# Vertical connections
# -------------------------
for x in [4, 8]:
    for y in range(0, 7, 2):
        ROAD_GRAPH.add_edge((x, y), (x, y + 2))

# -------------------------
# Curve connections
# -------------------------
for i in range(len(CURVE) - 1):
    ROAD_GRAPH.add_edge(CURVE[i], CURVE[i + 1])

# -------------------------
# Connect curve to grid
# -------------------------
ROAD_GRAPH.add_edge((10, 2), (10, 0))
ROAD_GRAPH.add_edge((10, 6), (10, 8))

# =========================
# HELPER FUNCTIONS
# =========================
def euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def nearest_node(pos):
    return min(ROAD_NODES, key=lambda n: euclid(pos, n))

print("ROAD NODES:", ROAD_NODES)

# =========================
# ROAD PHEROMONES
# =========================
ROAD_PHEROMONES = {}

INITIAL_PHEROMONE = 1.0

for node, neighbors in ROAD_GRAPH.graph.items():
    for nxt, _ in neighbors:
        edge = tuple(sorted((node, nxt)))
        ROAD_PHEROMONES[edge] = INITIAL_PHEROMONE
