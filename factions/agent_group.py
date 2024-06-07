import random
from agent import Agent
from vector2d import Vector2D

class AgentGroup:
    def __init__(self, world, num_agents, color, cohesion_weight, separation_weight, alignment_weight, wander_weight):
        self.agents = []
        self.world = world
        for i in range(num_agents):
            position = Vector2D(random.randint(0, world.width), random.randint(0, world.height))
            agent = Agent(world, position, color=color)
            agent.apply_behavior_weights(cohesion_weight, separation_weight, alignment_weight, wander_weight)
            self.agents.append(agent)

    def update(self, delta_time):
        for agent in self.agents:
            agent.update(delta_time)

    def render(self, screen):
        for agent in self.agents:
            agent.render(screen)

    def set_behavior_weights(self, cohesion, separation, alignment, wander):
        for agent in self.agents:
            agent.apply_behavior_weights(cohesion, separation, alignment, wander)
