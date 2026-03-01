import pygame

def render_sidebar_background(target_display_surface, grid_width, sidebar_width, grid_height, bg_color):
    """Renders the dark background container for the UI controls."""
    sidebar_bounding_rectangle = pygame.Rect(
        grid_width, 0, sidebar_width, max(grid_height, 600)
    )
    pygame.draw.rect(target_display_surface, bg_color, sidebar_bounding_rectangle)


def render_metrics_dashboard(
    target_display_surface, 
    app_state, 
    active_algo, 
    active_heur, 
    metrics_dict, 
    dynamic_mode_enabled,
    dimensions, 
    fonts, 
    colors
):
    """Draws the sidebar, including controls and live metrics."""
    grid_width, grid_height, sidebar_width = dimensions
    header_font, metric_font = fonts
    bg_color, text_color, highlight_color = colors

    # Draw the base sidebar background
    render_sidebar_background(target_display_surface, grid_width, sidebar_width, grid_height, bg_color)
    
    # Application State Header
    state_text = f"STATE: {app_state}"
    state_surface = header_font.render(state_text, True, highlight_color)
    target_display_surface.blit(state_surface, (grid_width + 20, 20))

    # Configuration Settings
    config_labels = [
        "--- CONFIGURATION ---",
        f"Algo: {active_algo}",
        f"Heur: {active_heur}",
        f"Dyn. Mode: {'ON' if dynamic_mode_enabled else 'OFF'}",
        "",
        "--- CONTROLS ---",
        "[A] Change Algorithm",
        "[H] Change Heuristic",
        "[Space] Start Search",
        "[C] Clear Grid",
        "[G] Generate Maze",
        "[D] Toggle Dynamic Mode",
        ""
    ]

    current_y_offset = 70
    for label in config_labels:
        color = highlight_color if "---" in label else text_color
        label_surface = metric_font.render(label, True, color)
        target_display_surface.blit(label_surface, (grid_width + 20, current_y_offset))
        current_y_offset += 25

    # Live Metrics
    metrics_labels = [
        "--- METRICS ---",
        f"Visited: {metrics_dict.get('visited_count', 0)}",
        f"Path Cost: {metrics_dict.get('path_cost', 0)}",
        f"Time: {metrics_dict.get('execution_time', 0.0):.2f} ms"
    ]
    
    for label in metrics_labels:
        color = highlight_color if "---" in label else text_color
        label_surface = metric_font.render(label, True, color)
        target_display_surface.blit(label_surface, (grid_width + 20, current_y_offset))
        current_y_offset += 25


def render_result_popup_overlay(
    target_display_surface, 
    metrics_dict, 
    dimensions, 
    fonts, 
    colors
):
    """Draws a pop-up in the lower right showing the final results."""
    grid_width, grid_height, sidebar_width = dimensions
    header_font, body_font = fonts
    bg_color, text_color, _ = colors # Highlight color replaced by dynamic success color

    popup_width, popup_height = 360, 220
    
    # Position: Lower Right of the entire window
    total_window_width = grid_width + sidebar_width
    popup_x = total_window_width - popup_width - 20
    popup_y = grid_height - popup_height - 20
    
    # Draw Background Box
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(target_display_surface, bg_color, popup_rect, border_radius=12)
    
    # Check Success/Failure State
    is_successful = metrics_dict.get("success", False)
    if is_successful:
        status_color = (0, 255, 100) # Green 
        header_text = "SEARCH SUCCESSFUL"
    else:
        status_color = (255, 50, 50) # Red
        header_text = "SEARCH FAILED"
        
    # Draw Border matching the state
    pygame.draw.rect(target_display_surface, status_color, popup_rect, width=3, border_radius=12)
    
    # Render Header Text
    header_surface = header_font.render(header_text, True, status_color)
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
        line_surface = body_font.render(line, True, text_color)
        target_display_surface.blit(line_surface, (popup_x + 25, popup_y + 65 + (i * 25)))
