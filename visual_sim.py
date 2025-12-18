import pygame
import sys
import time
import math

from ehive import EV, Station, init_pheromone, combine_and_assign

# =========================
# PYGAME SETUP
# =========================
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("E-Hive – Full Charging Lifecycle Simulation")

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
# PARAMETERS
# =========================
SPEED = 2.0
CHARGING_TIME = 5.0
EXIT_POINT = (50, 50)

# =========================
# EVs
# =========================
evs = [
    EV("EV1", 0.20, 120, 60, 1.0, 100, 200),
    EV("EV2", 0.80, 40, 50, 0.0, 100, 260),
    EV("EV3", 0.10, 150, 70, 1.0, 100, 320),
    EV("EV4", 0.50, 80, 45, 0.0, 100, 380),
]

# EV lifecycle state
for ev in evs:
    ev.charging = False
    ev.done = False
    ev.exiting = False
    ev.charge_start = None

# =========================
# STATIONS
# =========================
stations = [
    Station("S1", 50, 750, 240),
    Station("S2", 30, 750, 360),
]

station_busy = {st.station_id: None for st in stations}

# =========================
# HELPERS
# =========================
def move_towards(ev, target):
    dx = target[0] - ev.x
    dy = target[1] - ev.y
    dist = math.hypot(dx, dy)
    if dist < SPEED:
        return True
    ev.x += SPEED * dx / dist
    ev.y += SPEED * dy / dist
    return False

def get_active_evs(evs):
    return [ev for ev in evs if not ev.done and not ev.exiting]

# =========================
# INIT E-HIVE
# =========================
pher = init_pheromone(evs, stations)
active_evs = get_active_evs(evs)
pher, assignment, priorities, _ = combine_and_assign(active_evs, stations, pher)

# =========================
# MAIN LOOP
# =========================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)

    # Draw stations
    for st in stations:
        pygame.draw.rect(screen, GREEN, (st.x-18, st.y-18, 36, 36))
        label = FONT.render(st.station_id, True, BLACK)
        screen.blit(label, (st.x-15, st.y-40))

    # Update EVs
    for ev in evs:
        # -------------------------
        # EXITING
        # -------------------------
        if ev.exiting:
            move_towards(ev, EXIT_POINT)
            color = GRAY

        # -------------------------
        # CHARGING
        # -------------------------
        elif ev.charging:
            color = ORANGE
            if time.time() - ev.charge_start >= CHARGING_TIME:
                ev.charging = False
                ev.done = True
                ev.exiting = True
                ev.soc = 1.0

                # Free station
                for sid in station_busy:
                    if station_busy[sid] == ev.ev_id:
                        station_busy[sid] = None

                assignment[ev.ev_id] = None

                # Re-run E-Hive for remaining EVs
                active_evs = get_active_evs(evs)
                if active_evs:
                    pher, assignment, priorities, _ = combine_and_assign(
                        active_evs, stations, pher
                    )

        # -------------------------
        # MOVING TO STATION
        # -------------------------
        else:
            color = BLUE
            st_id = assignment.get(ev.ev_id)
            if st_id:
                st = next(s for s in stations if s.station_id == st_id)
                arrived = move_towards(ev, (st.x, st.y))

                if arrived and station_busy[st_id] is None:
                    ev.charging = True
                    ev.charge_start = time.time()
                    station_busy[st_id] = ev.ev_id

        pygame.draw.circle(screen, color, (int(ev.x), int(ev.y)), 10)

        label = FONT.render(
            f"{ev.ev_id} | SoC {int(ev.soc*100)}%",
            True, BLACK
        )
        screen.blit(label, (ev.x-45, ev.y-25))

    title = FONT.render(
        "E-Hive: Charge → Exit → Next EV (FINAL)",
        True, BLACK
    )
    screen.blit(title, (20, 10))

    pygame.display.flip()
    clock.tick(60)
