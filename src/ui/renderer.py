import pygame
from ui.constants import WHITE
from ui.grid_ui import render_node_to_surface, render_grid_structural_lines

# --- NEW: Import our modular UI functions ---
from ui.dashboard_ui import render_metrics_dashboard, render_result_popup_overlay

class ModernInformationRenderer:
    def __init__(self, grid_pixel_width, grid_pixel_height, sidebar_pixel_width):
        pygame.font.init()
        self.grid_pixel_width = grid_pixel_width
        self.grid_pixel_height = grid_pixel_height
        self.sidebar_pixel_width = sidebar_pixel_width
        
        # Typography
        self.dashboard_header_font = pygame.font.SysFont("inter", 24, bold=True)
        self.dashboard_metric_font = pygame.font.SysFont("monospace", 16)
        self.node_weight_font = pygame.font.SysFont("inter", 14, bold=True)
        
        # Colors
        self.node_text_color = (130, 130, 130)
        self.sidebar_background_color = (30, 30, 35)
        self.sidebar_text_color = (220, 220, 220)
        self.highlight_color = (64, 224, 208) # Turquoise for active selections
        
        # System settings passed from the main application
        self.dynamic_mode = False

    def draw_metrics_dashboard(self, target_display_surface, app_state, active_algorithm, active_heuristic, metrics_dict):
        """Delegates the sidebar drawing to the specialized dashboard_ui module."""
        render_metrics_dashboard(
            target_display_surface, 
            app_state, 
            active_algorithm, 
            active_heuristic, 
            metrics_dict,
            self.dynamic_mode,
            dimensions=(self.grid_pixel_width, self.grid_pixel_height, self.sidebar_pixel_width),
            fonts=(self.dashboard_header_font, self.dashboard_metric_font),
            colors=(self.sidebar_background_color, self.sidebar_text_color, self.highlight_color)
        )

    def draw_result_popup_overlay(self, target_display_surface, metrics_dict):
        """Delegates the pop-up drawing to the specialized dashboard_ui module."""
        render_result_popup_overlay(
            target_display_surface,
            metrics_dict,
            dimensions=(self.grid_pixel_width, self.grid_pixel_height, self.sidebar_pixel_width),
            fonts=(self.dashboard_header_font, self.dashboard_metric_font),
            colors=(self.sidebar_background_color, self.sidebar_text_color, self.highlight_color)
        )

    def render_complete_environment_frame(self, target_display_surface, environment_manager, agent_coords=None):
        target_display_surface.fill(WHITE)
        
        for current_node_row in environment_manager.grid_matrix:
            for individual_grid_node in current_node_row:
                render_node_to_surface(
                    target_display_surface, individual_grid_node, 
                    text_font=self.node_weight_font, text_color=self.node_text_color
                )
                
        render_grid_structural_lines(
            target_display_surface, environment_manager.total_row_count, 
            environment_manager.total_column_count, self.grid_pixel_width
        )
        
        # Draw the physical agent in transit
        if agent_coords:
            row, col = agent_coords
            node = environment_manager.grid_matrix[row][col]
            center_x = node.pixel_x_coordinate + (node.pixel_width // 2)
            center_y = node.pixel_y_coordinate + (node.pixel_width // 2)
            
            # Draw a dark blue circle representing the moving agent
            pygame.draw.circle(target_display_surface, (0, 0, 150), (center_x, center_y), node.pixel_width // 3)
