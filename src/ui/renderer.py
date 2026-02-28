import pygame
from ui.constants import WHITE
from ui.grid_ui import render_node_to_surface, render_grid_structural_lines

class ModernInformationRenderer:
    def __init__(self, grid_pixel_width, grid_pixel_height, sidebar_pixel_width):
        pygame.font.init()
        self.grid_pixel_width = grid_pixel_width
        self.grid_pixel_height = grid_pixel_height
        self.sidebar_pixel_width = sidebar_pixel_width
        
        # Typography for the dashboard
        self.dashboard_header_font = pygame.font.SysFont("inter", 24, bold=True)
        self.dashboard_metric_font = pygame.font.SysFont("monospace", 18)
        
        # Color palette for the modern sidebar
        self.sidebar_background_color = (30, 30, 35)
        self.sidebar_text_color = (220, 220, 220)

    def draw_sidebar_background(self, target_display_surface):
        """Renders the dark background container for the UI controls."""
        sidebar_bounding_rectangle = pygame.Rect(
            self.grid_pixel_width, 
            0, 
            self.sidebar_pixel_width, 
            max(self.grid_pixel_height, 600) # Ensures sidebar covers minimum height
        )
        pygame.draw.rect(target_display_surface, self.sidebar_background_color, sidebar_bounding_rectangle)

    def draw_metrics_dashboard(self, target_display_surface, visited_node_count, total_path_cost, execution_time_milliseconds):
        """Requirement: Real-Time Metrics Dashboard."""
        # Draw the background panel first
        self.draw_sidebar_background(target_display_surface)
        
        # Draw the Header
        header_text_surface = self.dashboard_header_font.render("METRICS", True, self.sidebar_text_color)
        target_display_surface.blit(header_text_surface, (self.grid_pixel_width + 20, 20))

        # Prepare the metric strings
        metrics_data_labels = [
            f"Nodes Visited: {visited_node_count}",
            f"Path Cost: {total_path_cost}",
            f"Time: {execution_time_milliseconds:.2f} ms"
        ]

        # Render and place each metric line
        for line_index, label_string in enumerate(metrics_data_labels):
            metric_text_surface = self.dashboard_metric_font.render(label_string, True, self.sidebar_text_color)
            target_display_surface.blit(
                metric_text_surface, 
                (self.grid_pixel_width + 20, 70 + (line_index * 35))
            )

    def render_complete_environment_frame(self, target_display_surface, environment_manager):
        """Orchestrates the drawing of the grid background, nodes, and structural lines."""
        # Clear the grid area
        target_display_surface.fill(WHITE)
        
        # Draw every individual node (The colored rectangles)
        for current_node_row in environment_manager.grid_matrix:
            for individual_grid_node in current_node_row:
                render_node_to_surface(target_display_surface, individual_grid_node)

        # Draw the structural grid lines over the nodes
        render_grid_structural_lines(
            target_display_surface, 
            environment_manager.total_row_count, 
            environment_manager.total_column_count,
            self.grid_pixel_width # Assuming the nodes scale proportionally based on width
        )
