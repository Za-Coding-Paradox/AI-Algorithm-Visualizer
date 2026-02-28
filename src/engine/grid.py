import pygame
import random
from ui.constants import *

class GridNode:
    def __init__(self, row_index, column_index, pixel_width, total_row_count, total_column_count):
        self.row_index = row_index
        self.column_index = column_index
        self.pixel_x_coordinate = row_index * pixel_width
        self.pixel_y_coordinate = column_index * pixel_width
        self.current_color = EMPTY_COLOR
        
        self.pixel_width = pixel_width
        self.total_row_count = total_row_count
        self.total_column_count = total_column_count
       
        self.movement_cost_weight = random.randint(1, 9)

        self.accessible_neighbors = []
        self.previous_traversal_node = None
        self.cost_from_start_node = float("inf")
        self.estimated_cost_to_goal_node = 0
        self.total_estimated_search_cost = float("inf")

    def get_grid_coordinates(self):
        return self.row_index, self.column_index

    def is_navigation_obstacle(self):
        return self.current_color == WALL_COLOR

    def reset_to_default_state(self):
        self.current_color = EMPTY_COLOR

    def set_as_agent_start(self):
        self.current_color = START_COLOR

    def set_as_navigation_goal(self):
        self.current_color = GOAL_COLOR

    def set_as_static_obstacle(self):
        self.current_color = WALL_COLOR

    def set_as_explored_node(self):
        self.current_color = VISITED_COLOR

    def set_as_frontier_node(self):
        self.current_color = FRONTIER_COLOR

    def set_as_final_path_segment(self):
        self.current_color = PATH_COLOR

    def identify_walkable_neighbors(self, full_grid_data):
        """Checks 4-way adjacency within rectangular bounds."""
        self.accessible_neighbors = []
        
        # Check Vertical Bounds (Rows)
        if self.row_index < self.total_row_count - 1:
            below = full_grid_data[self.row_index + 1][self.column_index]
            if not below.is_navigation_obstacle(): self.accessible_neighbors.append(below)

        if self.row_index > 0:
            above = full_grid_data[self.row_index - 1][self.column_index]
            if not above.is_navigation_obstacle(): self.accessible_neighbors.append(above)
                
        # Check Horizontal Bounds (Columns)
        if self.column_index < self.total_column_count - 1:
            right = full_grid_data[self.row_index][self.column_index + 1]
            if not right.is_navigation_obstacle(): self.accessible_neighbors.append(right)

        if self.column_index > 0:
            left = full_grid_data[self.row_index][self.column_index - 1]
            if not left.is_navigation_obstacle(): self.accessible_neighbors.append(left)
    

    def construct_initial_grid(total_row_count, total_column_count, display_width):
        """Requirement: Dynamic Grid Sizing."""

        grid_matrix = []
        node_pixel_dimension = display_width // total_row_count

        for current_row_index in range(total_row_count):
            grid_matrix.append([])
            
            for current_column_index in range(total_column_count):
                newly_created_node = GridNode(
                    current_row_index, 
                    current_column_index, 
                    node_pixel_dimension, 
                    total_row_count
                )
                grid_matrix[current_row_index].append(newly_created_node)
        return grid_matrix

    def generate_procedural_obstacles(grid_matrix, obstacle_probability_density=0.3):
        """Requirement: Random Map Generation."""
    
        for current_grid_row in grid_matrix:
            for individual_node in current_grid_row:
                if individual_node.current_color == EMPTY_COLOR and random.random() < obstacle_probability_density:
                    individual_node.set_as_static_obstacle()

