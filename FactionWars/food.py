import pygame
from vector2d import Vector2D
from random import randint

class Food:
    def __init__(self, world, position=None, radius=5, color=(0, 255, 0)):
        self.world = world
        self.radius = radius
        self.color = color
        self.position = position if position else self.spawn() 
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
    
    def spawn(self):
            while True:
                x = randint(0, self.world.width)
                y = randint(0, self.world.height)
                position = Vector2D(x, y)
                if not any(wall.rect.collidepoint(position.x, position.y) for wall in self.world.walls):
                    return position