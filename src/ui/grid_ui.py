import pygame
from ui.constants import GRID_LINE_COLOR

def render_grid_structural_lines(display_surface, total_rows, total_columns, grid_pixel_width):
    """Draws lines for a dynamic Rows x Columns grid."""
    
    # Node size is uniform, basically same for all nodes
    node_spacing = grid_pixel_width // max(total_rows, total_columns)

    # Draw Horizontal Lines based on Row Count
    for row_step in range(total_rows + 1):
        pygame.draw.line(
            display_surface, 
            GRID_LINE_COLOR, 
            (0, row_step * node_spacing), 
            (total_columns * node_spacing, row_step * node_spacing)
        )
        
    # Draw Vertical Lines based on Column Count
    for col_step in range(total_columns + 1):
        pygame.draw.line(
            display_surface, 
            GRID_LINE_COLOR, 
            (col_step * node_spacing, 0), 
            (col_step * node_spacing, total_rows * node_spacing)
        )
