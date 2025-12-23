from road_graph import RoadGraph

def create_simple_road_map():
    rg = RoadGraph()

    # Nodes 
    nodes = [
        (100, 200), (300, 200), (500, 200), (700, 200),
        (100, 350), (300, 350), (500, 350), (700, 350),
    ]

    for n in nodes:
        rg.add_node(n)

    # Horizontal roads
    rg.add_edge((100,200), (300,200))
    rg.add_edge((300,200), (500,200))
    rg.add_edge((500,200), (700,200))

    rg.add_edge((100,350), (300,350))
    rg.add_edge((300,350), (500,350))
    rg.add_edge((500,350), (700,350))

    # Vertical connectors
    rg.add_edge((300,200), (300,350))
    rg.add_edge((500,200), (500,350))

    return rg

