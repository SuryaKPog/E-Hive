from road_map import create_simple_road_map

rg = create_simple_road_map()

ev_node = (100, 200)
station_node = (700, 350)

dist = rg.shortest_path_distance(ev_node, station_node)
print("Road distance:", dist)
