import pygame
from world import World

class Game:
    def __init__(self, width=1200, height=1000):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Faction Wars')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30) 
        self.world = World(width, height) 

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(60) / 80.0  # Delta time in seconds, change to 200 for default !!

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.world.update(delta_time)
            self.world.render(self.screen)
            # FPS
            fps = int(self.clock.get_fps())
            fps_text = self.font.render(f"FPS: {fps}", True, pygame.Color('black'))
            self.screen.blit(fps_text, (10, 10))
            
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
