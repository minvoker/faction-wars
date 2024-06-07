from agent import Agent
from vector2d import Vector2D
from random import randint

class AgentGroup:
    def __init__(self, world, num_agents, color, cohesion_weight, separation_weight, alignment_weight, wander_weight):
        self.agents = []
        self.world = world
        self.color = color
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.wander_weight = wander_weight
        #self.goals = goals

        for i in range(num_agents):
            position = Vector2D(randint(0, world.width), randint(0, world.height))
            agent = Agent(world, position, self, color=color, mode='wander')
            agent.apply_behavior_weights(cohesion_weight, separation_weight, alignment_weight, wander_weight)
            self.agents.append(agent)

    def update(self, delta_time):
        for agent in self.agents:
            agent.update(delta_time)

    def render(self, screen):
        for agent in self.agents:
            agent.render(screen)

    def get_agents(self):
        return self.agents
