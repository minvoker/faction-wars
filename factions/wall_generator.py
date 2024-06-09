''' Generate interesting walls for the simulation '''
import pygame
import random
#from random import randint, choice, random

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
        
    def generate_walls(self): # Meh
            walls = []
            num_walls = 40  

            for _ in range(num_walls):
                while True:
                    x = random.randint(0, self.width - self.wall_thickness)
                    y = random.randint(0, self.height - self.wall_thickness)
                    wall_width = random.randint(self.wall_thickness, self.width // 4)
                    wall_height = random.randint(self.wall_thickness, self.height // 4)

                    # Check if the wall overlaps
                    if self.is_valid_wall_position(x, y, wall_width, wall_height):
                        walls.append(Wall(self.world, (x, y), wall_width, wall_height))
                        break

            return walls

    def is_valid_wall_position(self, x, y, wall_width, wall_height):
            # King zones
            kzone1_x, kzone1_y, kzone1_width, kzone1_height = self.world.kzone1
            kzone2_x, kzone2_y, kzone2_width, kzone2_height = self.world.kzone2

            # Center area
            center_x = self.width // 2
            center_y = self.height // 2
            center_width = self.width // 5
            center_height = self.height // 5

            # Top and bottom lanes
            lane_height = self.height // 20
            top_lane_y = 0
            bottom_lane_y = self.height - lane_height

            def overlaps(zone_x, zone_y, zone_width, zone_height):
                return not (x + wall_width < zone_x or x > zone_x + zone_width or
                            y + wall_height < zone_y or y > zone_y + zone_height)

            if overlaps(kzone1_x, kzone1_y, kzone1_width, kzone1_height):
                return False
            if overlaps(kzone2_x, kzone2_y, kzone2_width, kzone2_height):
                return False
            if overlaps(center_x - center_width // 2, center_y - center_height // 2, center_width, center_height):
                return False
            if overlaps(0, top_lane_y, self.width, lane_height):
                return False
            if overlaps(0, bottom_lane_y, self.width, lane_height):
                return False

            return True

        
class Wall:
    def __init__(self, world, position, width, height):
        self.world = world
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.color = (0, 0, 0)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)