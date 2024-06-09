''' Generate interesting walls for the simulation '''
import pygame
from random import randint, choice, random

class WallGenerator:
    def __init__(self, world, wall_thickness=20):
        self.world = world
        start_zone_size = world.start_zone_size
        self.width = world.width
        self.height = world.height 
        self.wall_thickness = wall_thickness
        
        self.generate = self.generate_walls() # gen walls
        
        self.test_walls = [
            Wall(self, (start_zone_size, start_zone_size), self.width - 3 * start_zone_size, wall_thickness),
            Wall(self, (start_zone_size, self.height - start_zone_size - wall_thickness), self.width - 2 * start_zone_size, wall_thickness),
            Wall(self, (start_zone_size, start_zone_size), wall_thickness, self.height - 3 * start_zone_size),
            Wall(self, (self.width - start_zone_size - wall_thickness, start_zone_size), wall_thickness, self.height - 2 * start_zone_size),
        ]
        
    def generate_walls(self):
        width = self.world.width
        height = self.world.height
        start_zone_size = self.world.start_zone_size

        # Define grid 
        grid_size = 10
        grid_tile_width = width // grid_size
        grid_tile_height = height // grid_size
        maze_walls = []

        # Create grid tiles with random openings
        for row in range(grid_size):
            for col in range(grid_size):
                tile_x = col * grid_tile_width
                tile_y = row * grid_tile_height

                # Don't create walls inside the king zones
                if (
                    (tile_x < start_zone_size and tile_y < start_zone_size) or
                    (tile_x > width - start_zone_size - grid_tile_width and tile_y > height - start_zone_size - grid_tile_height)
                ):
                    continue

                # Determine the openings for the current tile (Higher value = more openings)
                top_open = random() < 0.7
                right_open = random() < 0.7
                bottom_open = random() < 0.7
                left_open = random() < 0.7

                # Create walls for the current tile based on the openings
                if not top_open and row > 0:
                    maze_walls.append(Wall(self.world, (tile_x, tile_y), grid_tile_width, self.wall_thickness))
                if not right_open and col < grid_size - 1:
                    maze_walls.append(Wall(self.world, (tile_x + grid_tile_width - self.wall_thickness, tile_y), self.wall_thickness, grid_tile_height))
                if not bottom_open and row < grid_size - 1:
                    maze_walls.append(Wall(self.world, (tile_x, tile_y + grid_tile_height - self.wall_thickness), grid_tile_width, self.wall_thickness))
                if not left_open and col > 0:
                    maze_walls.append(Wall(self.world, (tile_x, tile_y), self.wall_thickness, grid_tile_height))

        # Create openings in the center tiles
        center_row = grid_size // 2
        center_col = grid_size // 2
        center_tile_x = center_col * grid_tile_width
        center_tile_y = center_row * grid_tile_height

        for wall in maze_walls:
            if ( # 3 default
                center_tile_x <= wall.rect.left < center_tile_x + 4 * grid_tile_width and
                center_tile_y <= wall.rect.top < center_tile_y + 4 * grid_tile_height
            ):
                maze_walls.remove(wall)

        return maze_walls

        
    
    def is_valid_map(self, walls):
        # Ensure a path exists between king zones, DFS with explored set?
        # From zone 1 to zone 2 
        explored = {}
        
        return True 
        
class Wall:
    def __init__(self, world, position, width, height):
        self.world = world
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.color = (0, 0, 0)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)