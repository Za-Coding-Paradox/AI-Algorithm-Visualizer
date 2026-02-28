import pygame
from ui.constants import WHITE
from ui.grid_ui import render_node_to_surface, render_grid_structural_lines

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
        
        # Pop-up Typography
        self.popup_header_font = pygame.font.SysFont("inter", 32, bold=True)
        self.popup_body_font = pygame.font.SysFont("inter", 20)
        
        # Colors
        self.node_text_color = (130, 130, 130)
        self.sidebar_background_color = (30, 30, 35)
        self.sidebar_text_color = (220, 220, 220)
        self.highlight_color = (64, 224, 208) # Turquoise for active selections

    def draw_sidebar_background(self, target_display_surface):
        sidebar_bounding_rectangle = pygame.Rect(
            self.grid_pixel_width, 0, self.sidebar_pixel_width, max(self.grid_pixel_height, 600)
        )
        pygame.draw.rect(target_display_surface, self.sidebar_background_color, sidebar_bounding_rectangle)

    def draw_metrics_dashboard(self, target_display_surface, app_state, active_algorithm, active_heuristic, metrics_dict):
        """Draws the sidebar, including controls and live metrics."""
        self.draw_sidebar_background(target_display_surface)
        
        # Application State Header
        state_text = f"STATE: {app_state}"
        state_surface = self.dashboard_header_font.render(state_text, True, self.highlight_color)
        target_display_surface.blit(state_surface, (self.grid_pixel_width + 20, 20))

        # Configuration Settings (Algorithm & Heuristic)
        config_labels = [
            "--- CONFIGURATION ---",
            f"Algo: {active_algorithm}",
            f"Heur: {active_heuristic}",
            "",
            "--- CONTROLS ---",
            "[A] Change Algorithm",
            "[H] Change Heuristic",
            "[Space] Start Search",
            "[C] Clear Grid",
            "[G] Generate Maze",
            ""
        ]

        current_y_offset = 70
        for label in config_labels:
            text_color = self.highlight_color if "---" in label else self.sidebar_text_color
            label_surface = self.dashboard_metric_font.render(label, True, text_color)
            target_display_surface.blit(label_surface, (self.grid_pixel_width + 20, current_y_offset))
            current_y_offset += 25

        # Live Metrics
        metrics_labels = [
            "--- METRICS ---",
            f"Visited: {metrics_dict.get('visited_count', 0)}",
            f"Path Cost: {metrics_dict.get('path_cost', 0)}",
            f"Time: {metrics_dict.get('execution_time', 0.0):.2f} ms"
        ]
        
        for label in metrics_labels:
            text_color = self.highlight_color if "---" in label else self.sidebar_text_color
            label_surface = self.dashboard_metric_font.render(label, True, text_color)
            target_display_surface.blit(label_surface, (self.grid_pixel_width + 20, current_y_offset))
            current_y_offset += 25

    def draw_result_popup_overlay(self, target_display_surface, metrics_dict):
        """Draws a pop-up in the lower right showing the final results, maintaining grid visibility."""
        
        popup_width, popup_height = 360, 220
        
        # Position: Lower Right of the entire window
        total_window_width = self.grid_pixel_width + self.sidebar_pixel_width
        popup_x = total_window_width - popup_width - 20
        popup_y = self.grid_pixel_height - popup_height - 20
        
        # Draw Background Box
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(target_display_surface, self.sidebar_background_color, popup_rect, border_radius=12)
        
        # Check Success/Failure State
        is_successful = metrics_dict.get("success", False)
        if is_successful:
            status_color = (0, 255, 100) # Green 
            header_text = "SEARCH SUCCESSFUL"
        else:
            status_color = (255, 50, 50) # Red
            header_text = "SEARCH FAILED (NO PATH)"
            
        # Draw Border matching the state
        pygame.draw.rect(target_display_surface, status_color, popup_rect, width=3, border_radius=12)
        
        # Render Header Text
        header_surface = self.dashboard_header_font.render(header_text, True, status_color)
        target_display_surface.blit(header_surface, (popup_x + 25, popup_y + 20))
        
        # Render Body Stats
        body_lines = [
            f"Total Nodes Visited: {metrics_dict.get('visited_count', 0)}",
            f"Final Path Cost: {metrics_dict.get('path_cost', 0)}",
            f"Compute Time: {metrics_dict.get('execution_time', 0.0):.2f} ms",
            "",
            "Press [C] to clear and reset."
        ]
        
        for i, line in enumerate(body_lines):
            line_surface = self.dashboard_metric_font.render(line, True, self.sidebar_text_color)
            target_display_surface.blit(line_surface, (popup_x + 25, popup_y + 65 + (i * 25)))

    def render_complete_environment_frame(self, target_display_surface, environment_manager):
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
