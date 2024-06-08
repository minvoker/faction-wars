import pygame
from vector2d import Vector2D
from random import randint

class Food:
    def __init__(self, world, position=None, radius=5, color=(0, 255, 0)):
        self.world = world
        self.radius = radius
        self.color = color
        if position is None:
            self.position = Vector2D(randint(0, world.width), randint(0, world.height))
        else:
            self.position = position
        self.being_held_by = None

    def update(self):
        if self.being_held_by: # If being held by agent, drop it
            self.position = self.being_held_by.position + Vector2D(self.radius /2 , self.radius / 2)

    def render(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)

    def add_touching_agent(self, agent):
        if not self.being_held_by:
            if not self.is_in_king_zone(agent.group):
                self.being_held_by = agent

    def is_in_king_zone(self, group=None):
        groups = [self.world.group1, self.world.group2]
        for g in groups:
            x, y, width, height = g.king_zone
            if x <= self.position.x <= x + width and y <= self.position.y <= y + height:
                if group is None or group == g:
                    return True
        return False