# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

from __future__ import annotations
# some of these types are deprecated: https://www.python.org/dev/peps/pep-0585/
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
T = TypeVar('T')

Location = TypeVar('Location')
class Graph(Protocol):
    def neighbors(self, id: Location) -> list[Location]: pass

class SimpleGraph:
    def __init__(self):
        self.edges: dict[Location, list[Location]] = {}
    
    def neighbors(self, id: Location) -> list[Location]:
        return self.edges[id]

example_graph = SimpleGraph()
example_graph.edges = {
    'A': ['B'],
    'B': ['C'],
    'C': ['B', 'D', 'F'],
    'D': ['C', 'E'],
    'E': ['F'],
    'F': [],
}

import collections

class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, x: T):
        self.elements.append(x)
    
    def get(self) -> T:
        return self.elements.popleft()

# utility functions for dealing with square grids
def from_id_width(id, width):
    return (id % width, id // width)

def draw_tile(graph, id, style):
    # Códigos de cor ANSI
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET_COLOR = "\033[0m"

    r = " . " # Padrão
    if 'number' in style and id in style['number']: r = " %-2d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = " > "
        if x2 == x1 - 1: r = " < "
        if y2 == y1 + 1: r = " v "
        if y2 == y1 - 1: r = " ^ "

    # Se for parte do caminho, define 'r' com o '@' verde
    if 'path' in style and id in style['path']:
        r = f" {GREEN}@{RESET_COLOR} " # Espaço, @ verde, Reset, Espaço

    # Se for o ponto inicial, define 'r' como ' A ' (sobrescreve 'path' se o início estiver no caminho)
    if 'start' in style and id == style['start']:
        r = " A "

    # Se for o ponto final, define 'r' como ' Z ' (sobrescreve 'path' ou 'start')
    if 'goal' in style and id == style['goal']:
        r = " Z "

    # Se for uma parede, define 'r' como '###' vermelho (sobrescreve qualquer estado anterior de 'r' para este tile)
    if id in graph.walls:
        r = f"{RED}###{RESET_COLOR}" # ### vermelho

    return r

def draw_grid(graph, **style):
    print("___" * graph.width)
    for y in range(graph.height):
        for x in range(graph.width):
            # A função draw_tile agora retorna a string com as cores ANSI
            print("%s" % draw_tile(graph, (x, y), style), end="")
        print()
    print("~~~" * graph.width)

# data from main article
DIAGRAM1_WALLS = [from_id_width(id, width=30) for id in [21,22,51,52,81,82,93,94,111,112,123,124,133,134,141,142,153,154,163,164,171,172,173,174,175,183,184,193,194,201,202,203,204,205,213,214,223,224,243,244,253,254,273,274,283,284,303,304,313,314,333,334,343,344,373,374,403,404,433,434]]

GridLocation = Tuple[int, int]

class SquareGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.walls: list[GridLocation] = []

    def in_bounds(self, id: GridLocation) -> bool:
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id: GridLocation) -> bool:
        return id not in self.walls

    def neighbors(self, id: GridLocation) -> Iterator[GridLocation]:
        (x, y) = id
        neighbors_coords = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)] # E W N S
        if (x + y) % 2 == 0: neighbors_coords.reverse() # S N W E
        results = filter(self.in_bounds, neighbors_coords)
        results = filter(self.passable, results)
        return results

class WeightedGraph(Graph): # Certifique-se que Graph está definido ou importado
    def cost(self, from_id: Location, to_id: Location) -> float: pass

class GridWithWeights(SquareGrid): # Herda de SquareGrid
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.weights: Dict[GridLocation, float] = {}
        # Lista para armazenar definições de áreas: {'rect': (xmin, ymin, xmax, ymax), 'cost': float}
        self.area_definitions: List[Dict] = []

    def add_cost_area(self, x_min: int, y_min: int, x_max: int, y_max: int, area_cost: float):
        """
        Define uma área retangular no grid com um custo de movimento específico.

        Args:
            x_min: Coordenada X mínima da área (inclusiva).
            y_min: Coordenada Y mínima da área (inclusiva).
            x_max: Coordenada X máxima da área (inclusiva).
            y_max: Coordenada Y máxima da área (inclusiva).
            area_cost: O custo para entrar em qualquer célula dentro desta área.
        """
        # Validação básica para garantir que a área está dentro dos limites (opcional, mas bom)
        if not (0 <= x_min < self.width and 0 <= y_min < self.height and
                x_min <= x_max < self.width and y_min <= y_max < self.height):
            print(f"Aviso: Área ({x_min},{y_min})-({x_max},{y_max}) com custo {area_cost} "
                  f"está parcial ou totalmente fora dos limites do grid ({self.width}x{self.height}).")
            # Você pode optar por levantar um erro aqui ou apenas avisar.
        self.area_definitions.append({'rect': (x_min, y_min, x_max, y_max), 'cost': area_cost})
        print(f"Adicionada área de custo: ({x_min},{y_min})-({x_max},{y_max}), custo={area_cost}")


    def cost(self, from_node: GridLocation, to_node: GridLocation) -> float:
        """
        Retorna o custo de se mover PARA 'to_node'.
        Prioridade:
        1. Custo da primeira área definida que contém 'to_node'.
        2. Se não estiver em nenhuma área, custo de self.weights.get(to_node, 1.0).
        """
        node_x, node_y = to_node

        # Verificar se to_node está dentro de alguma área definida
        # A ordem importa: a primeira área na lista que contém o nó determinará o custo.
        # Se áreas se sobrepuserem, a que foi adicionada primeiro (e corresponde) terá precedência.
        for area_def in self.area_definitions:
            rect_x_min, rect_y_min, rect_x_max, rect_y_max = area_def['rect']
            area_specific_cost = area_def['cost']

            if rect_x_min <= node_x <= rect_x_max and rect_y_min <= node_y <= rect_y_max:
                return area_specific_cost # Custo da área

        # Se não estiver em nenhuma área especial, usa os pesos individuais ou o padrão
        return self.weights.get(to_node, 1.0)

diagram4 = GridWithWeights(10, 10)
diagram4.walls = [(1, 7), (1, 8), (2, 7), (2, 8), (3, 7), (3, 8)]
diagram4.weights = {loc: 5 for loc in [(3, 4), (3, 5), (4, 1), (4, 2),
                                       (4, 3), (4, 4), (4, 5), (4, 6),
                                       (4, 7), (4, 8), (5, 1), (5, 2),
                                       (5, 3), (5, 4), (5, 5), (5, 6),
                                       (5, 7), (5, 8), (6, 2), (6, 3),
                                       (6, 4), (6, 5), (6, 6), (6, 7),
                                       (7, 3), (7, 4), (7, 5)]}

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]

def dijkstra_search(graph: WeightedGraph, start: Location, goal: Location):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

# thanks to @m1sp <Jaiden Mispy> for this simpler version of
# reconstruct_path that doesn't have duplicate entries

def reconstruct_path(came_from: dict[Location, Location],
                     start: Location, goal: Location) -> list[Location]:

    current: Location = goal
    path: list[Location] = []
    if goal not in came_from: # no path was found
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path

diagram_nopath = GridWithWeights(10, 10)
diagram_nopath.walls = [(5, row) for row in range(10)]

def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph: WeightedGraph, start: Location, goal: Location):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

def breadth_first_search(graph: Graph, start: Location, goal: Location):
    frontier = Queue()
    frontier.put(start)
    came_from: dict[Location, Optional[Location]] = {}
    came_from[start] = None
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current
    
    return came_from

class SquareGridNeighborOrder(SquareGrid):
    def neighbors(self, id):
        (x, y) = id
        neighbors = [(x + dx, y + dy) for (dx, dy) in self.NEIGHBOR_ORDER]
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return list(results)

def test_with_custom_order(neighbor_order):
    if neighbor_order:
        g = SquareGridNeighborOrder(30, 15)
        g.NEIGHBOR_ORDER = neighbor_order
    else:
        g = SquareGrid(30, 15)
    g.walls = DIAGRAM1_WALLS
    start, goal = (8, 7), (27, 2)
    came_from = breadth_first_search(g, start, goal)
    draw_grid(g, path=reconstruct_path(came_from, start=start, goal=goal),
              point_to=came_from, start=start, goal=goal)

class GridWithAdjustedWeights(GridWithWeights):
    def cost(self, from_node, to_node):
        prev_cost = super().cost(from_node, to_node)
        nudge = 0
        (x1, y1) = from_node
        (x2, y2) = to_node
        if (x1 + y1) % 2 == 0 and x2 != x1: nudge = 1
        if (x1 + y1) % 2 == 1 and y2 != y1: nudge = 1
        return prev_cost + 0.001 * nudge