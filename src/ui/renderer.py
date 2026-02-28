import pygame
from ui.constants import *
from engine.grid import draw_grid_structure_lines

class ModernInformationRenderer:
    def __init__(self, grid_size, sidebar_width):
        pygame.font.init()
        self.grid_size = grid_size
        self.sidebar_width = sidebar_width
        # Professional fonts for UI clarity
        self.header_font = pygame.font.SysFont("inter", 24, bold=True)
        self.metric_font = pygame.font.SysFont("monospace", 18)
        
        # UI Colors for a modern look
        self.sidebar_background_color = (30, 30, 35)
        self.sidebar_text_color = (220, 220, 220)

    def draw_sidebar_background(self, target_surface):
        """Draws the dark sidebar container."""
        sidebar_rectangle = pygame.Rect(self.grid_size, 0, self.sidebar_width, self.grid_size)
        pygame.draw.rect(target_surface, self.sidebar_background_color, sidebar_rectangle)

    def draw_metrics_dashboard(self, target_surface, visited_count, path_cost, time_ms):
        """Requirement: Real-Time Metrics Dashboard."""
        self.draw_sidebar_background(target_surface)
        
        header_surface = self.header_font.render("METRICS", True, self.sidebar_text_color)
        target_surface.blit(header_surface, (self.grid_size + 20, 20))

        metrics_labels = [
            f"Nodes Visited: {visited_count}",
            f"Path Cost: {path_cost}",
            f"Time: {time_ms:.2f}ms"
        ]

        for index, label in enumerate(metrics_labels):
            text_surface = self.metric_font.render(label, True, self.sidebar_text_color)
            target_surface.blit(text_surface, (self.grid_size + 20, 70 + (index * 35)))

    def draw_environment_state(self, target_surface, environment_manager):
        """Requirement: Mandatory Visualization elements."""
        # Clear background
        target_surface.fill(WHITE)
        
        # Render every GridNode
        for grid_row in environment_manager.grid_matrix:
            for individual_node in grid_row:
                individual_node.render_to_surface(target_surface)

        # Draw grid line overlay
        draw_grid_structure_lines(
            target_surface, 
            environment_manager.total_row_count, 
            self.grid_size
        )
