import random
from ui.constants import EMPTY_COLOR

class DynamicObstacleManager:
    @staticmethod
    def attempt_spawn_obstacle(environment_manager, spawn_probability=0.03):
        """
        Requirement: Spawning Logic.
        Spawns a new obstacle on the grid with a small probability at every time step.
        """
        if random.random() > spawn_probability:
            return None
            
        empty_nodes = [
            node for row in environment_manager.grid_matrix for node in row 
            if node.current_color == EMPTY_COLOR 
        ]
        
        if not empty_nodes:
            return None
            
        spawned_node = random.choice(empty_nodes)
        spawned_node.set_as_static_obstacle()
        return spawned_node.get_grid_coordinates()

    @staticmethod
    def is_collision_on_path(spawned_coords, remaining_path_coords):
        """
        Requirement: Efficiency.
        Avoids resetting the entire search if the obstacle is not on the current path.
        """
        return spawned_coords in remaining_path_coords

    @staticmethod
    def trigger_replanning(environment_manager, current_agent_coords, algo_func, heur_func):
        """
        Requirement: Re-planning Mechanism.
        Immediately calculates a new path to the target from the current position.
        """
        original_start = environment_manager.agent_start_node
        
        # Temporarily move the Start Node to the Agent's current location
        curr_row, curr_column = current_agent_coords
        environment_manager.agent_start_node = environment_manager.grid_matrix[curr_row][curr_column]
        
        # Clear old visual path colors (but keep walls)
        environment_manager.clear_search_visuals()
        
        # Calculate new path
        new_execution_trace = algo_func(environment_manager, heur_func)
        
        # Restore the original start point
        environment_manager.agent_start_node = original_start
        
        return new_execution_trace
