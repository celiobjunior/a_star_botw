import random # Necessário para populate_enemies_randomly
from typing import Tuple, Optional, List, TypeVar, Set # Adicionando type hints faltantes para populate_enemies_randomly

# Supondo que o resto do seu código (A*, GridWithWeights, draw_grid, etc.)
# está em src.implementation ou definido acima.
from src.implementation import * # Isso deve incluir GridWithWeights, a_star_search, reconstruct_path, draw_grid

# --- Definição da função para popular inimigos (coloque-a aqui ou importe-a) ---
# Se já estiver em src.implementation, você não precisa redefini-la aqui.
# Vou incluí-la para o exemplo ser autocontido.

# Location = TypeVar('Location') # Provavelmente já definido em src.implementation
GridLocation = Tuple[int, int] # Provavelmente já definido em src.implementation

def populate_enemies_randomly(grid: SquareGrid, num_enemies: int,
                              start_pos: Optional[GridLocation] = None,
                              goal_pos: Optional[GridLocation] = None) -> None:
    if not hasattr(grid, 'walls'):
        raise TypeError("O objeto grid deve ter um atributo 'walls'.")
    grid.walls = []
    available_cells: Set[GridLocation] = set()
    for x_coord in range(grid.width):
        for y_coord in range(grid.height):
            available_cells.add((x_coord, y_coord))
    if start_pos and start_pos in available_cells: available_cells.remove(start_pos)
    if goal_pos and goal_pos in available_cells: available_cells.remove(goal_pos)
    if num_enemies > len(available_cells):
        raise ValueError(f"Células disponíveis insuficientes ({len(available_cells)}) para {num_enemies} inimigos.")
    grid.walls.extend(random.sample(list(available_cells), num_enemies))


if __name__ == "__main__":
    GRID_WIDTH = 50
    GRID_HEIGHT = 50
    NUM_ENEMIES = 700 # Reduzi um pouco para aumentar a chance de encontrar caminho com áreas de custo

    g = GridWithWeights(GRID_WIDTH, GRID_HEIGHT)

    # --- Definir Áreas de Custo ---
    # Área 1: Um "rio" lento no meio, custo 5
    # x_min, y_min, x_max, y_max, cost
    g.add_cost_area(0, GRID_HEIGHT // 2 - 2, GRID_WIDTH - 1, GRID_HEIGHT // 2 + 2, 2.0)

    # Área 2: Uma "montanha" cara no canto superior direito, custo 10
    g.add_cost_area(GRID_WIDTH // 2, 0, GRID_WIDTH - 1, GRID_HEIGHT // 2 - 1, 5.0)

    # Área 3: Um "pântano" no canto inferior esquerdo, custo 7
    g.add_cost_area(0, GRID_HEIGHT // 2 + 3, GRID_WIDTH // 2 -1 , GRID_HEIGHT - 1, 7.0)

    # Área 4: Um "atalho rápido" (mas talvez perigoso se tiver inimigos), custo 0.5
    # Este é um pequeno quadrado, vamos colocá-lo em algum lugar que não sobreponha muito
    # ou que demonstre sobreposição.
    # Se sobrepor, a primeira área adicionada que contém o nó terá seu custo aplicado.
    g.add_cost_area(10, 10, 15, 15, 1)

    # (Opcional) Adicionar alguns pesos individuais para células específicas,
    # se elas não estiverem cobertas por áreas ou se você quiser um custo muito específico.
    # g.weights[(5,5)] = 20 # Custo alto para uma célula específica

    # --- Definir Início e Fim ---
    start: GridLocation = (30, 49)  # Canto superior esquerdo, por exemplo
    goal: GridLocation = (2, 16)

    # --- Popular com Inimigos (Paredes) ---
    try:
        populate_enemies_randomly(g, NUM_ENEMIES, start_pos=start, goal_pos=goal)
        print(f"{len(g.walls)} inimigos/paredes posicionados aleatoriamente.")
    except ValueError as e:
        print(f"Erro ao popular o grid: {e}")
        exit()

    # --- Executar A* ---
    print(f"Procurando caminho de {start} para {goal}...")
    came_from, cost_so_far = a_star_search(g, start, goal) # Supondo que a_star_search está definida

    path = reconstruct_path(came_from, start=start, goal=goal) # Supondo que reconstruct_path está definida

    # --- Desenhar Grid ---
    # Supondo que draw_grid e outras funções de desenho/heurística estão definidas
    if not path:
        print(f"Nenhum caminho encontrado de {start} para {goal}.")
        # Mesmo sem caminho, desenhar para ver a configuração
        draw_grid(g, start=start, goal=goal)
    else:
        print(f"Caminho encontrado com {len(path)} passos.")
        # Opcional: Adicionar números de custo ao draw_grid para visualização
        # Isso exigiria modificar a função draw_tile e draw_grid
        style_args = {
            'point_to': came_from,
            'path': path,
            'start': start,
            'goal': goal,
            # 'number': cost_so_far # Descomente se draw_tile/draw_grid suportar isso
            # 'costs_map': g # Para que draw_tile possa acessar g.cost() ou g.area_definitions
        }
        draw_grid(g, **style_args)

    print(f"Custo total do caminho até o objetivo: {cost_so_far.get(goal, float('inf'))}")