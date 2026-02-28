import random
from engine.grid import construct_initial_grid, generate_procedural_obstacles

class SimulationEnvironment:
    def __init__(self, total_row_count, total_column_count, display_pixel_width):
        """
        Requirement: Dynamic Grid Sizing (Rows x Columns).
        Initializes the agent's environment as a rectangular matrix of GridNodes.
        """
        self.total_row_count = total_row_count
        self.total_column_count = total_column_count
        self.display_pixel_width = display_pixel_width
        
        # Calculate the size of each node based on the largest dimension to fit the window
        self.individual_node_pixel_size = display_pixel_width // max(total_row_count, total_column_count)
        
        self.agent_start_node = None
        self.navigation_goal_node = None
        
        # Initialize the 2D grid matrix
        self.grid_matrix = []
        
        for current_row_index in range(total_row_count):
            # Create a new list for the current row
            current_row_data = []
            
            for current_column_index in range(total_column_count):
                # Instantiate a new node with descriptive parameters
                newly_created_node = GridNode(
                    current_row_index, 
                    current_column_index, 
                    self.individual_node_pixel_size, 
                    total_row_count, 
                    total_column_count
                )
                current_row_data.append(newly_created_node)
            
            # Add the completed row to the master grid matrix
            self.grid_matrix.append(current_row_data)

    def reset_environment_state(self):
        """Clears the entire grid while preserving the dimensions."""
        self.grid_matrix = construct_initial_grid(self.total_row_count, self.display_pixel_width)
        self.agent_start_node = None
        self.navigation_goal_node = None

    def generate_random_maze(self, obstacle_density=0.3):
        """Requirement: Random Map Generation with user-defined density."""
        # Ensure we don't wipe the start/goal if they already exist
        generate_procedural_obstacles(self.grid_matrix, obstacle_density)
        
        # Re-apply Start and Goal colors if they were overwritten by random logic
        if self.agent_start_node:
            self.agent_start_node.set_as_agent_start()
        if self.navigation_goal_node:
            self.navigation_goal_node.set_as_navigation_goal()

    def handle_manual_node_placement(self, row_index, column_index):
        """Requirement: Interactive Map Editor (Placement logic)."""
        selected_node = self.grid_matrix[row_index][column_index]

        # Place Start Node first
        if not self.agent_start_node and selected_node != self.navigation_goal_node:
            self.agent_start_node = selected_node
            self.agent_start_node.set_as_agent_start()
        
        # Place Goal Node second
        elif not self.navigation_goal_node and selected_node != self.agent_start_node:
            self.navigation_goal_node = selected_node
            self.navigation_goal_node.set_as_navigation_goal()
        
        # Place Obstacles thereafter
        elif selected_node != self.navigation_goal_node and selected_node != self.agent_start_node:
            selected_node.set_as_static_obstacle()

    def handle_manual_node_removal(self, row_index, column_index):
        """Requirement: Interactive Map Editor (Removal logic)."""
        selected_node = self.grid_matrix[row_index][column_index]
        selected_node.reset_to_default_state()

        if selected_node == self.agent_start_node:
            self.agent_start_node = None
        elif selected_node == self.navigation_goal_node:
            self.navigation_goal_node = None

    def get_environment_data(self):
        """Returns the core components needed by search algorithms or the UI."""
        return {
            "grid": self.grid_matrix,
            "start": self.agent_start_node,
            "goal": self.navigation_goal_node
        }
