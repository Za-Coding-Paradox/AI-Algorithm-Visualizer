import pygame

class ApplicationDisplayWindow:
    def __init__(self, total_window_width, total_window_height, window_caption="AI Algorithm Visualizer"):
        """Initializes the main Pygame display surface."""
        self.total_window_width = total_window_width
        self.total_window_height = total_window_height
        
        self.main_display_surface = pygame.display.set_mode(
            (self.total_window_width, self.total_window_height)
        )
        pygame.display.set_caption(window_caption)

    def refresh_display_state(self):
        """Pushes the back-buffer drawing to the user's screen."""
        pygame.display.flip()

    def get_main_surface(self):
        """Provides the surface object for the renderer to draw upon."""
        return self.main_display_surface
