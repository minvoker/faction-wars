import pygame
from agent_group import AgentGroup
from matrix33 import Matrix33

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Add two groups of agents, lags around 500 each
        self.group1 = AgentGroup(self, 200, (255, 0, 0), 1.0, 1.0, 1.0, 1.0)
        self.group2 = AgentGroup(self, 200, (0, 0, 255), 1.0, 1.0, 1.0, 1.0)

    def update(self, delta_time):
        self.group1.update(delta_time)
        self.group2.update(delta_time)

    def render(self, screen):
        screen.fill((255, 255, 255))  # Bg white
        self.group1.render(screen)
        self.group2.render(screen)
        pygame.display.flip()

    def get_all_agents(self):
        return self.group1.get_agents() + self.group2.get_agents()

    def get_group_agents(self, group_number): # Get own faciton agents
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
