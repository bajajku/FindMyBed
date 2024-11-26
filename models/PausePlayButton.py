import pygame
from utils.constants import BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, PAUSED_COLOR, PLAY_COLOR

class PausePlayButton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BUTTON_WIDTH
        self.height = BUTTON_HEIGHT
        self.paused = False

    def draw(self, screen):
        # Draw the button on the screen with different colors based on state
        button_color = PLAY_COLOR if self.paused else PAUSED_COLOR
        pygame.draw.rect(screen, button_color, (self.x, self.y, self.width, self.height))

        # Render the button text (Pause/Play)
        font = pygame.font.Font(None, 36)
        text = "Play" if self.paused else "Pause"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
                                   self.y + (self.height - text_surface.get_height()) // 2))

    def toggle(self, screen):
        self.paused = not self.paused
        self.draw(screen)

    def is_clicked(self, pos):
        """Check if the button is clicked."""
        x, y = pos
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
