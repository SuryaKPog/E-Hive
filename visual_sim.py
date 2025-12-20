import pygame
import sys
import time
import math

from ehive import EV, Station, init_pheromone, combine_and_assign, ROAD_GRAPH, ROAD_NODES

# =========================
# PYGAME SETUP
# =========================
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("E-Hive – Road-Based EV Movement")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 16)

# =========================
# COLORS
# =========================
WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (60,130,255)
GREEN = (0,180,0)
ORANGE = (255,165,0)
GRAY = (180,180,180)

# =========================
# SCALE (🔥 IMPORTANT FIX)
# =========================
SCALE = 70
OFFSET_X = 100
OFFSET_Y = 100

def to_screen(pos):
    x, y = pos
    return int(x * SCALE + OFFSET_X), int(y * SCALE + OFFSET_Y)

# =========================
# PARAMETERS
# =========================
SPEED = 0.05   # world units per frame
CHARGING_TIME = 4.0
EXIT_POINT = (-1, -1)

# =========================
# HELPER FUNCTIONS
# =========================
def euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def nearest_node(pos):
    return min(ROAD_NODES, key=lambda n: euclid(pos, n))

def shortest_path_nodes(start, end):
    import heapq
    pq = [(0, start, [start])]
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)
        if node == end:
            return path
        if node in visited:
            continue
        visited.add(node)
        for nxt, w in ROAD_GRAPH.graph[node]:
            if nxt not in visited:
                heapq.heappush(pq, (cost + w, nxt, path + [nxt]))
    return []

def move_towards(ev, target):
    dx = target[0] - ev.x
    dy = target[1] - ev.y
    dist = math.hypot(dx, dy)
    if dist < SPEED:
        ev.x, ev.y = target
        return True
    ev.x += SPEED * dx / dist
    ev.y += SPEED * dy / dist
    return False

# =========================
# EVs (WORLD COORDS)
# =========================
evs = [
    EV("EV1", 0.20, 120, 60, 1.0, 0, 0),
    EV("EV2", 0.80, 40, 50, 0.0, 2, 0),
    EV("EV3", 0.10, 150, 70, 1.0, 0, 5),
    EV("EV4", 0.50, 80, 45, 0.0, 3, 5),
]

for ev in evs:
    ev.charging = False
    ev.done = False
    ev.exiting = False
    ev.path = []
    ev.path_index = 0
    ev.charge_start = None

# =========================
# STATIONS (WORLD COORDS)
# =========================
stations = [
    Station("S1", 50, 10, 0),
    Station("S2", 30, 10, 5),
]

station_busy = {st.station_id: None for st in stations}

# =========================
# INIT E-HIVE
# =========================
pher = init_pheromone(evs, stations)
active_evs = [ev for ev in evs if not ev.done]
pher, assignment, _, _ = combine_and_assign(active_evs, stations, pher)

# =========================
# MAIN LOOP
# =========================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)

    # -------------------------
    # DRAW ROADS (SCALED)
    # -------------------------
    for node, neighbors in ROAD_GRAPH.graph.items():
        for nxt, _ in neighbors:
            pygame.draw.line(
                screen,
                BLACK,
                to_screen(node),
                to_screen(nxt),
                4
            )

    # -------------------------
    # DRAW STATIONS
    # -------------------------
    for st in stations:
        sx, sy = to_screen((st.x, st.y))
        pygame.draw.rect(screen, GREEN, (sx-15, sy-15, 30, 30))
        screen.blit(FONT.render(st.station_id, True, BLACK), (sx-15, sy-35))

    # -------------------------
    # UPDATE EVs
    # -------------------------
    for ev in evs:
        if ev.exiting:
            move_towards(ev, EXIT_POINT)
            color = GRAY

        elif ev.charging:
            color = ORANGE
            if time.time() - ev.charge_start >= CHARGING_TIME:
                ev.charging = False
                ev.done = True
                ev.exiting = True
                ev.soc = 1.0
                for sid in station_busy:
                    if station_busy[sid] == ev.ev_id:
                        station_busy[sid] = None

                active_evs = [e for e in evs if not e.done and not e.exiting]
                if active_evs:
                    pher, assignment, _, _ = combine_and_assign(
                        active_evs, stations, pher
                    )

        else:
            color = BLUE
            st_id = assignment.get(ev.ev_id)
            if st_id:
                st = next(s for s in stations if s.station_id == st_id)

                if not ev.path:
                    start = nearest_node((ev.x, ev.y))
                    end = nearest_node((st.x, st.y))
                    ev.path = shortest_path_nodes(start, end)
                    ev.path_index = 0

                if ev.path_index < len(ev.path):
                    reached = move_towards(ev, ev.path[ev.path_index])
                    if reached:
                        ev.path_index += 1
                else:
                    if station_busy[st_id] is None:
                        ev.charging = True
                        ev.charge_start = time.time()
                        station_busy[st_id] = ev.ev_id

        px, py = to_screen((ev.x, ev.y))
        pygame.draw.circle(screen, color, (px, py), 10)
        screen.blit(
            FONT.render(f"{ev.ev_id} {int(ev.soc*100)}%", True, BLACK),
            (px-30, py-25)
        )

    screen.blit(
        FONT.render("E-Hive: Road-Constrained EV Coordination", True, BLACK),
        (20, 10)
    )

    pygame.display.flip()
    clock.tick(60)