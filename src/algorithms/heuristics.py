import math

def calculate_manhattan_distance(current_node, target_node):
    """
    Requirement: Manhattan Distance.
    Formula: D_manhattan = |x1 - x2| + |y1 - y2|
    """
    current_x, current_y = current_node.get_grid_coordinates()
    target_x, target_y = target_node.get_grid_coordinates()
    
    vertical_distance = abs(current_x - target_x)
    horizontal_distance = abs(current_y - target_y)
    
    return vertical_distance + horizontal_distance

def calculate_euclidean_distance(current_node, target_node):
    """
    Requirement: Euclidean Distance.
    Formula: D_euclidean = sqrt((x1 - x2)^2 + (y1 - y2)^2)
    """
    current_x, current_y = current_node.get_grid_coordinates()
    target_x, target_y = target_node.get_grid_coordinates()
    
    vertical_difference_squared = (current_x - target_x) ** 2
    horizontal_difference_squared = (current_y - target_y) ** 2
    
    return math.sqrt(vertical_difference_squared + horizontal_difference_squared)
