from agent import Agent, KingAgent
from vector2d import Vector2D
from random import randint

class AgentGroup:
    def __init__(self, world, num_agents, color, cohesion_weight, separation_weight, alignment_weight, wander_weight, king_zone=None):
        self.agents = []
        self.world = world
        self.color = color
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.wander_weight = wander_weight
        self.king_zone = king_zone
        self.goal = None
        self.world_target = None
        
        if king_zone:
            king_pos = self.get_valid_position(king_zone)
            king = KingAgent(world, king_pos, self, self.king_zone, color=color)
            self.agents.append(king)

            for i in range(num_agents):
                position = self.get_valid_position(king_zone)
                agent = Agent(world, position, self, color=color, mode='wander')
                agent.apply_behavior_weights(self.cohesion_weight, self.separation_weight, self.alignment_weight, self.wander_weight)
                self.agents.append(agent)
        else:
            raise ValueError("King zone must be specified to spawn agents")

    def get_valid_position(self, zone):
        while True:
            x = randint(zone[0], zone[0] + zone[2])
            y = randint(zone[1], zone[1] + zone[3])
            position = Vector2D(x, y)
            if not self.is_position_in_wall(position):
                return position

    def is_position_in_wall(self, position):
        for wall in self.world.walls:
            if wall.rect.collidepoint(position.x, position.y):
                return True
        return False

    def update(self, delta_time):
        if self.goal == 'attack':
            self.attack()
        elif self.goal == 'retreat':
            self.retreat()
        for agent in self.agents[:]:  # Iterate over a copy of the list
            if not agent.alive:
                self.agents.remove(agent)
            else:
                agent.update(delta_time)

    def render(self, screen):
        for agent in self.agents:
            agent.render(screen)

    def attack(self):
        # Command all agents to start attack mode
        for agent in self.agents:
            agent.start_attack(self.world_target)

    def apply_behavior_weights(self, cohesion_weight, separation_weight, alignment_weight, wander_weight):
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.wander_weight = wander_weight

        for agent in self.agents:
            agent.apply_behavior_weights(cohesion_weight, separation_weight, alignment_weight, wander_weight)