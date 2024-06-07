import pygame
from world import World

class Game:
    def __init__(self, width=1200, height=1000):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Faction Wars')
        self.clock = pygame.time.Clock()
        self.world = World(width, height)

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(60) / 100.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.world.update(delta_time)
            self.world.render(self.screen)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
