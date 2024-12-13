import pygame
from utils.constants import BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, PAUSED_COLOR, PLAY_COLOR

class PausePlayButton:
    """
    A class representing a Pause/Play button in a Pygame simulation.

    Attributes:
        x (int): The x-coordinate of the button's top-left corner.
        y (int): The y-coordinate of the button's top-left corner.
        width (int): The width of the button, defined in `utils.constants`.
        height (int): The height of the button, defined in `utils.constants`.
        paused (bool): The current state of the button, where True indicates "paused" and False indicates "playing".
    """
    def __init__(self, x, y):
        """
        Initialize the PausePlayButton with its position and default state.

        Args:
            x (int): The x-coordinate of the button's top-left corner.
            y (int): The y-coordinate of the button's top-left corner.
        """
        self.x = x
        self.y = y
        self.width = BUTTON_WIDTH
        self.height = BUTTON_HEIGHT
        self.paused = False

    def draw(self, screen):
        """
        Draw the button on the Pygame screen with different colors and text
        based on its current state.

        Args:
            screen (pygame.Surface): The Pygame screen to draw the button on.
        """
        # Determine the button color based on the paused state
        button_color = PLAY_COLOR if self.paused else PAUSED_COLOR
        pygame.draw.rect(screen, button_color, (self.x, self.y, self.width, self.height))

        # Render the button text (Pause/Play)
        font = pygame.font.Font(None, 36)
        text = "Play" if self.paused else "Pause"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
                                   self.y + (self.height - text_surface.get_height()) // 2))

    def toggle(self, screen):
        """
        Toggle the button's state between "paused" and "play" and redraw the button.

        Args:
            screen (pygame.Surface): The Pygame screen to redraw the button on.
        """
        self.paused = not self.paused
        self.draw(screen)

    def is_clicked(self, pos):
        """
        Check if the button is clicked based on the given mouse position.

        Args:
            pos (tuple): A tuple of (x, y) coordinates of the mouse click.

        Returns:
            bool: True if the button was clicked, False otherwise.
        """
        x, y = pos
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
