import pygame
from agent import Agent
from vector2d import Vector2D
from random import randint

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.groups = []

    def add_group(self, group):
        self.groups.append(group)

    def update(self, delta_time):
        for group in self.groups:
            group.update(delta_time)

    def render(self, screen):
        screen.fill((255, 255, 255))  # Bg white
        for group in self.groups:
            group.render(screen)
        pygame.display.flip()

    # Maybe keep for later.....
    def wrap_around(self, position):
        if position.x < 0:
            position.x = self.width
        elif position.x > self.width:
            position.x = 0
        if position.y < 0:
            position.y = self.height
        elif position.y > self.height:
            position.y = 0
