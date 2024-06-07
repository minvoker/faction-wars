import pygame
from world import World
from agent_group import AgentGroup

class Game:
    def __init__(self, width=1200, height=1000):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Faction Wars')
        self.clock = pygame.time.Clock()
        self.world = World(width, height)

        # Create groups with different initial weights
        group1 = AgentGroup(self.world, num_agents=10, color=(255, 0, 0), cohesion_weight=1.0, separation_weight=1.0, alignment_weight=1.0, wander_weight=1.0)
        group2 = AgentGroup(self.world, num_agents=10, color=(0, 0, 255), cohesion_weight=0.5, separation_weight=1.5, alignment_weight=0.5, wander_weight=1.0)
        
        self.world.add_group(group1)
        self.world.add_group(group2)

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(60) / 10.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.world.update(delta_time)
            self.world.render(self.screen)

        pygame.quit()

