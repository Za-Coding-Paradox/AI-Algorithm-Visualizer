import pygame
from ui.constants import * 

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

def render_node_to_surface(display_surface, node_object, text_font=None, text_color=(150, 150, 150)):
    """Draws a single node's colored rectangle and its terrain weight onto the surface."""
    
    # Draw the base square
    pygame.draw.rect(
        display_surface, 
        node_object.current_color, 
        (
            node_object.pixel_x_coordinate, 
            node_object.pixel_y_coordinate, 
            node_object.pixel_width,
            node_object.pixel_width
        )
    )

    # Draw the weight text 
    if text_font and node_object.current_color != WALL_COLOR:
        # Convert the integer weight to a string
        weight_string = str(node_object.movement_cost_weight)
        
        # Create the text image
        text_surface = text_font.render(weight_string, True, TEXT_COLOR)
        
        # Calculate the exact center of this specific node
        node_center_x = node_object.pixel_x_coordinate + (node_object.pixel_width // 2)
        node_center_y = node_object.pixel_y_coordinate + (node_object.pixel_width // 2)
        
        # Create a bounding box for the text and snap its center to the node's center
        text_bounding_box = text_surface.get_rect(center=(node_center_x, node_center_y))
        
        # Blit (copy) the text onto the screen
        display_surface.blit(text_surface, text_bounding_box)
