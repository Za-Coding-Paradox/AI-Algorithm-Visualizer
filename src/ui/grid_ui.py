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
            (0, row_step * node_spacing),                           # start_pos (x, y) 
            (total_columns * node_spacing, row_step * node_spacing) # end_pos (x, y)
        )
        
    # Draw Vertical Lines based on Column Count
    for col_step in range(total_columns + 1):
        pygame.draw.line(
            display_surface, 
            GRID_LINE_COLOR, 
            (col_step * node_spacing, 0), 
            (col_step * node_spacing, total_rows * node_spacing)
        )

def render_node_to_surface(display_surface, node_object):
    """Draws a single node's colored rectangle onto the surface."""
    pygame.draw.rect(
        display_surface, 
        node_object.current_color, 
        (
            node_object.pixel_x_coordinate, 
            node_object.pixel_y_coordinate, 
            node_object.pixel_width,        # height
            node_object.pixel_width         # width
        )
    )
