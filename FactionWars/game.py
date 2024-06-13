import pygame
from vector2d import Vector2D
from world import World

class Slider: # For changing agent behaviour weights in real time
    def __init__(self, x, y, width, height, min_val, max_val, start_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.handle_rect = pygame.Rect(x + (start_val - min_val) / (max_val - min_val) * width - 5, y, 10, height)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.value = (event.pos[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val) + self.min_val
                self.handle_rect.x = event.pos[0]
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0] and self.handle_rect.collidepoint(event.pos):
                self.value = (event.pos[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val) + self.min_val
                self.handle_rect.x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))

    def draw(self, screen):
        pygame.draw.rect(screen, (240, 240, 240), self.rect)  # Slider background
        pygame.draw.rect(screen, (0, 0, 0), self.handle_rect)  # Slider selector

class Game:
    def __init__(self, width=1000, height=800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Faction Wars')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.count = pygame.font.Font(None, 22)
        self.world = World(width, height)

        # Sliders for groups behaviour weights
        self.sliders = {
            'cohesion_group1': Slider(width - 150, 50, 150, 10, 0, 1, self.world.group1.cohesion_weight),
            'separation_group1': Slider(width - 150, 70, 150, 10, 0, 1, self.world.group1.separation_weight),
            'alignment_group1': Slider(width - 150, 90, 150, 10, 0, 1, self.world.group1.alignment_weight),
            'wander_group1': Slider(width - 150, 110, 150, 10, 0, 1, self.world.group1.wander_weight),
            'cohesion_group2': Slider(width - 150, 150, 150, 10, 0, 1, self.world.group2.cohesion_weight),
            'separation_group2': Slider(width - 150, 170, 150, 10, 0, 1, self.world.group2.separation_weight),
            'alignment_group2': Slider(width - 150, 190, 150, 10, 0, 1, self.world.group2.alignment_weight),
            'wander_group2': Slider(width - 150, 210, 150, 10, 0, 1, self.world.group2.wander_weight),
            'max_speed': Slider(width - 150, 300, 150, 10, 1, 25, 10),
        }

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(60) / 80.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                for slider in self.sliders.values():
                    slider.update(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right-click
                    target = Vector2D(event.pos[0], event.pos[1])
                    self.world.group1.world_target = target
                    self.world.group2.world_target = target
                    self.world.group1.attack()
                    self.world.group2.attack()
                       
                        
            # Update weights based on slider values
            self.world.group1.apply_behavior_weights(
                self.sliders['cohesion_group1'].value,
                self.sliders['separation_group1'].value,
                self.sliders['alignment_group1'].value,
                self.sliders['wander_group1'].value,
            )
            self.world.group2.apply_behavior_weights(
                self.sliders['cohesion_group2'].value,
                self.sliders['separation_group2'].value,
                self.sliders['alignment_group2'].value,
                self.sliders['wander_group2'].value,
            )
            max_speed = self.sliders['max_speed'].value
            for agent in self.world.group1.agents + self.world.group2.agents:
                agent.max_speed = max_speed

            self.world.update(delta_time)
            self.world.render(self.screen)

            # Text
            fps = int(self.clock.get_fps())
            fps_text = self.font.render(f"FPS: {fps}", True, pygame.Color('black'))
            self.screen.blit(fps_text, (10, 10))

            group1 = len(self.world.group1.agents)
            group2 = len(self.world.group2.agents)
            counts = self.count.render(f"Red: {group1} Blue {group2}", True, pygame.Color('black'))
            self.screen.blit(counts, (430, 10))

            # Draw sliders
            for slider in self.sliders.values():
                slider.draw(self.screen)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
