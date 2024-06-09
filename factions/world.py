import pygame
from agent_group import AgentGroup
from matrix33 import Matrix33
from food import Food
from wall_generator import WallGenerator

class World:
    def __init__(self, width, height, num_food):
        self.width = width
        self.height = height
        
        # Define start zones in the corners
        self.start_zone_size = min(width, height) // 5
        start_zone_size = self.start_zone_size

        self.kzone1 = (0, 0, start_zone_size, start_zone_size)
        self.kzone2 = (width - start_zone_size, height - start_zone_size, start_zone_size, start_zone_size)
        
        # Add walls
        self.walls = WallGenerator(self).generate
        
        # Add two groups of agents, lags around 500 each
        self.group1 = AgentGroup(self, 200, (255, 0, 0), 0.4, 1.0, 1.0, 1.0, self.kzone1)
        self.group2 = AgentGroup(self, 200, (0, 0, 255), 0.4, 1.0, 1.0, 1.0, self.kzone2)
        
        self.food = [Food(self) for _ in range(num_food)]
        
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
        return self.group1.get_agents() + self.group2.get_agents()

    def get_group_agents(self, group_number): # Get own faction agents
        if group_number == 1:
            return self.group1.get_agents()
        elif group_number == 2:
            return self.group2.get_agents()
        else:
            return []

    def get_other_group_agents(self, group): # Get other faction agents
        if group == self.group1:
            return self.group2.get_agents()
        elif group == self.group2:
            return self.group1.get_agents()
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

