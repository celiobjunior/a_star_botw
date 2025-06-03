from implementation import *

g = SquareGrid(50, 50)
g.walls = DIAGRAM1_WALLS

start = (8, 7)
goal = (17, 2)
parents = breadth_first_search(g, start, goal)
draw_grid(g, point_to=parents, start=start, goal=goal)