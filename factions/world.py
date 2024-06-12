import pygame
from agent_group import AgentGroup
from matrix33 import Matrix33
from food import Food
from wall_generator import WallGenerator
from astar import Node, a_star_search 
from vector2d import Vector2D

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Define start zones in the corners
        self.start_zone_size = min(width, height) // 5
        start_zone_size = self.start_zone_size

        self.kzone1 = (0, 0, start_zone_size, start_zone_size)
        self.kzone2 = (width - start_zone_size, height - start_zone_size, start_zone_size, start_zone_size)
        
        # Add walls
        self.walls = WallGenerator(self).test_walls
        
        # Add two groups of agents, lags around 500 each
        # AGENT GROUP CONSTRUCTOR cohesion_weight, separation_weight, alignment_weight, wander_weight
        self.group1 = AgentGroup(self, 200, (255, 0, 0), 0.1, 0.5, 0.4, 0.8, self.kzone1)
        self.group2 = AgentGroup(self, 200, (0, 0, 255), 0.3, 1.0, 0.3, 1.0, self.kzone2)
        
        # Add Food
        self.num_food = 30
        self.food = [Food(self) for _ in range(self.num_food)]
        
        # Grid overlay for path planning 
        self.cell_size = 30 # Some values break it...
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size
        self.grid = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        self.initialize_grid()
        
    def update(self, delta_time):
        self.group1.update(delta_time)
        self.group2.update(delta_time)
        for food in self.food:
            food.update()

    def render(self, screen):
        screen.fill((255, 255, 255))  # Bg white
        self.draw_king_zones(screen)
        for wall in self.walls:
            wall.render(screen)
        for food in self.food:
            food.render(screen)
        self.group1.render(screen)
        self.group2.render(screen)
        
    def draw_king_zones(self, screen):
        x, y, width, height = self.kzone1
        pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height), 2)
        
        x, y, width, height = self.kzone2
        pygame.draw.rect(screen, (0, 0, 255), (x, y, width, height), 2)

    def get_all_agents(self):
        return self.group1.agents + self.group2.agents

    def get_group_agents(self, group_number): # Get own faction agents
        if group_number == 1:
            return self.group1.agents
        elif group_number == 2:
            return self.group2.agents
        else:
            return []

    def get_other_group_agents(self, group): # Get other faction agents
        if group == self.group1:
            return self.group2.agents
        elif group == self.group2:
            return self.group1.agents
        else:
            return []

    def transform_points(self, points, pos, forward, side, scale):
        wld_pts = [pt.copy() for pt in points]
        mat = Matrix33()
        mat.scale_update(scale.x, scale.y)
        mat.rotate_by_vectors_update(forward, side)
        mat.translate_update(pos.x, pos.y)
        mat.transform_vector2d_list(wld_pts)
        return wld_pts

    # Grid and planning stuff
    def initialize_grid(self):
        for wall in self.walls:
            rect = wall.rect
            start_grid_x = max(0, rect.x // self.cell_size)
            start_grid_y = max(0, rect.y // self.cell_size)
            end_grid_x = min(self.grid_width - 1, (rect.x + rect.width) // self.cell_size)
            end_grid_y = min(self.grid_height - 1, (rect.y + rect.height) // self.cell_size)

            for x in range(start_grid_x, end_grid_x + 1):
                for y in range(start_grid_y, end_grid_y + 1):
                    self.grid[x][y] = 1  # Marking grid cells as occupied by walls
            
    def get_neighbors(self, state):
        grid_x, grid_y = state
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, right, up, down
        for dx, dy in directions:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height and self.grid[nx][ny] == 0:
                neighbors.append((nx, ny))
        return neighbors
        
    def step_cost(self, state, action):
        return 1

    def heuristic(self, state, goal): # Manhattan
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    
    def plan_path(self, start, goal):
        start_grid = (int(start.x) // self.cell_size, int(start.y) // self.cell_size)
        goal_grid = (int(goal.x) // self.cell_size, int(goal.y) // self.cell_size)

        result_node, _ = a_star_search(start_grid, goal_grid, self.get_neighbors, self.step_cost, self.heuristic)

        if result_node is None:
            return []  # No path found

        # Reconstruct path
        path = result_node.path()
        return [Vector2D(x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2) for x, y in path]
