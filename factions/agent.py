import pygame
from vector2d import Vector2D
from random import uniform, randint, choice
from math import sin, cos, radians

class Agent:
    def __init__(self, world, position, radius=5, color=(255, 0, 0), scale=1, mass=0.6):
        self.world = world
        self.position = position
        self.velocity = Vector2D(uniform(-1, 1), uniform(-1, 1))
        self.radius = radius
        self.color = color
        self.scale = scale
        self.mass = mass

        # Behavior weights
        self.cohesion_weight = 1.0
        self.separation_weight = 1.0
        self.alignment_weight = 1.0
        self.wander_weight = 1.0

    def update(self, delta_time):
        self.position += self.velocity * delta_time
        self.check_bounds()

    def check_bounds(self):
        if self.position.x - self.radius < 0:
            self.position.x = self.radius
            self.velocity.x *= -1
        elif self.position.x + self.radius > self.world.width:
            self.position.x = self.world.width - self.radius
            self.velocity.x *= -1

        if self.position.y - self.radius < 0:
            self.position.y = self.radius
            self.velocity.y *= -1
        elif self.position.y + self.radius > self.world.height:
            self.position.y = self.world.height - self.radius
            self.velocity.y *= -1

    def apply_behavior_weights(self, cohesion, separation, alignment, wander):
        self.cohesion_weight = cohesion
        self.separation_weight = separation
        self.alignment_weight = alignment
        self.wander_weight = wander

    def render(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
