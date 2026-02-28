import pygame
import sys
from engine.environment import SimulationEnvironment
from ui.window import ApplicationDisplayWindow
from ui.renderer import ModernInformationRenderer

def translate_mouse_position_to_grid_indices(mouse_pixel_position, row_limit, column_limit, grid_pixel_width):
    """Translates a raw screen pixel click into (row_index, column_index)."""

    node_pixel_gap = grid_pixel_width // max(row_limit, column_limit)
    horizontal_mouse_x, vertical_mouse_y = mouse_pixel_position
    
    # Divide the pixel coordinate by the gap to find the grid index
    target_column_index = horizontal_mouse_x // node_pixel_gap
    target_row_index = vertical_mouse_y // node_pixel_gap
    
    return int(target_row_index), int(target_column_index)

class PathfindingVisualizerApp:
    def __init__(self, total_row_count=40, total_column_count=40, grid_pixel_dimension=800, sidebar_pixel_dimension=250):
        """Initializes all sub-systems required for the visualizer."""
        pygame.init()
        
        self.total_row_count = total_row_count
        self.total_column_count = total_column_count
        self.grid_pixel_dimension = grid_pixel_dimension
        
        # Calculate total window size (Grid + Sidebar)
        self.total_window_width = grid_pixel_dimension + sidebar_pixel_dimension
        self.total_window_height = grid_pixel_dimension
        
        # 1. Initialize Window
        self.display_window = ApplicationDisplayWindow(
            self.total_window_width, 
            self.total_window_height, 
            "AI Pathfinding Visualizer"
        )
        
        # 2. Initialize Environment (The Data)
        self.environment_manager = SimulationEnvironment(
            self.total_row_count, 
            self.total_column_count, 
            self.grid_pixel_dimension
        )
        
        # 3. Initialize Renderer (The Visuals)
        self.information_renderer = ModernInformationRenderer(
            self.grid_pixel_dimension, 
            self.total_window_height, 
            sidebar_pixel_dimension
        )

    def run_application_loop(self):
        """The main execution loop that handles events and rendering."""
        application_is_running = True
        
        # Placeholder metrics (Will be updated by search algorithms later)
        current_nodes_visited_count = 0
        current_path_cost = 0
        current_execution_time_milliseconds = 0.0

        while application_is_running:
            # --- RENDER PHASE ---
            target_display_surface = self.display_window.get_main_surface()
            
            self.information_renderer.render_complete_environment_frame(
                target_display_surface, 
                self.environment_manager
            )
            
            self.information_renderer.draw_metrics_dashboard(
                target_display_surface,
                current_nodes_visited_count,
                current_path_cost,
                current_execution_time_milliseconds
            )
            
            self.display_window.refresh_display_state()

            # --- EVENT HANDLING PHASE ---
            for current_event in pygame.event.get():
                # Handle Window Close
                if current_event.type == pygame.QUIT:
                    application_is_running = False
                    pygame.quit()
                    sys.exit()

                # Handle Left Mouse Click (Place Start/Goal/Wall)
                if pygame.mouse.get_pressed()[0]:
                    current_mouse_position = pygame.mouse.get_pos()
                    
                    # Ensure the user is clicking inside the grid, not the sidebar
                    if current_mouse_position[0] < self.grid_pixel_dimension:
                        target_row_index, target_column_index = translate_mouse_position_to_grid_indices(
                            current_mouse_position, 
                            self.total_row_count, 
                            self.total_column_count, 
                            self.grid_pixel_dimension
                        )
                        self.environment_manager.handle_manual_node_placement(target_row_index, target_column_index)

                # Handle Right Mouse Click (Remove Node)
                elif pygame.mouse.get_pressed()[2]:
                    current_mouse_position = pygame.mouse.get_pos()
                    
                    if current_mouse_position[0] < self.grid_pixel_dimension:
                        target_row_index, target_column_index = translate_mouse_position_to_grid_indices(
                            current_mouse_position, 
                            self.total_row_count, 
                            self.total_column_count, 
                            self.grid_pixel_dimension
                        )
                        self.environment_manager.handle_manual_node_removal(target_row_index, target_column_index)

                # Handle Keyboard Input
                if current_event.type == pygame.KEYDOWN:
                    if current_event.key == pygame.K_c:
                        # 'C' clears the board
                        self.environment_manager.reset_environment_state()
                    
                    if current_event.key == pygame.K_g:
                        # 'G' generates random obstacles
                        self.environment_manager.generate_random_maze(obstacle_density=0.3)

def execute_visualizer():
    """The single run function to be imported into main.py."""
    main_application_instance = PathfindingVisualizerApp()
    main_application_instance.run_application_loop()
