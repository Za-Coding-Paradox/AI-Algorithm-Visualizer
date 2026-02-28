import pygame
import sys
import time

from engine.environment import SimulationEnvironment
from ui.window import ApplicationDisplayWindow
from ui.renderer import ModernInformationRenderer
from ui.algorithm_ui import apply_trace_action_to_environment

# Import the Algorithms and Heuristics
from algorithms.a_star import execute_a_star_search
from algorithms.greedy_bfs import execute_greedy_best_first_search
from algorithms.heuristics import calculate_manhattan_distance, calculate_euclidean_distance

# Application States Constants
APP_STATE_IDLE = "IDLE"
APP_STATE_RUNNING = "RUNNING"
APP_STATE_RESULT = "RESULT"

def translate_mouse_position_to_grid_indices(mouse_pixel_position, row_limit, column_limit, grid_pixel_width):
    node_pixel_gap = grid_pixel_width // max(row_limit, column_limit)

    # Mouse X (horizontal) maps to the Grid's Row Index
    target_row_index = mouse_pixel_position[0] // node_pixel_gap
    # Mouse Y (vertical) maps to the Grid's Column Index
    target_column_index = mouse_pixel_position[1] // node_pixel_gap

    return int(target_row_index), int(target_column_index)

class PathfindingVisualizerApp:
    def __init__(self, total_row_count=40, total_column_count=40, grid_pixel_dimension=800, sidebar_pixel_dimension=300):
        pygame.init()
        self.total_row_count = total_row_count
        self.total_column_count = total_column_count
        self.grid_pixel_dimension = grid_pixel_dimension
        
        self.display_window = ApplicationDisplayWindow(
            grid_pixel_dimension + sidebar_pixel_dimension, grid_pixel_dimension, "AI Pathfinding Visualizer"
        )
        self.environment_manager = SimulationEnvironment(total_row_count, total_column_count, grid_pixel_dimension)
        self.information_renderer = ModernInformationRenderer(grid_pixel_dimension, grid_pixel_dimension, sidebar_pixel_dimension)
        
        # STATE MACHINE VARIABLES
        self.current_app_state = APP_STATE_IDLE
        
        # ALGORITHM SETTINGS
        self.available_algorithms = {"A* Search": execute_a_star_search, "Greedy BFS": execute_greedy_best_first_search}
        self.available_heuristics = {"Manhattan": calculate_manhattan_distance, "Euclidean": calculate_euclidean_distance}
        
        self.algorithm_names = list(self.available_algorithms.keys())
        self.heuristic_names = list(self.available_heuristics.keys())
        
        self.current_algo_index = 0
        self.current_heur_index = 0
        
        # EXECUTION TRACE & METRICS 
        self.active_execution_trace = []
        self.metrics_data = {"visited_count": 0, "path_cost": 0, "execution_time": 0.0}

    def run_application_loop(self):
        application_is_running = True
        clock = pygame.time.Clock()

        while application_is_running:
            target_display_surface = self.display_window.get_main_surface()
            
            # RENDER BASE ENVIRONMENT
            self.information_renderer.render_complete_environment_frame(target_display_surface, self.environment_manager)
            
            # RENDER SIDEBAR METRICS & CONTROLS
            active_algo_name = self.algorithm_names[self.current_algo_index]
            active_heur_name = self.heuristic_names[self.current_heur_index]
            
            self.information_renderer.draw_metrics_dashboard(
                target_display_surface, self.current_app_state, 
                active_algo_name, active_heur_name, self.metrics_data
            )
            
            # RENDER RESULT POPUP (If applicable)
            if self.current_app_state == APP_STATE_RESULT:
                self.information_renderer.draw_result_popup_overlay(target_display_surface, self.metrics_data)

            self.display_window.refresh_display_state()

            # RUNNING STATE LOGIC (Trace Playback)
            # --- RUNNING STATE LOGIC (Trace Playback) ---
            if self.current_app_state == APP_STATE_RUNNING:
                if len(self.active_execution_trace) > 0:
                    steps_per_frame = 5 
                    for _ in range(min(steps_per_frame, len(self.active_execution_trace))):
                        trace_step = self.active_execution_trace.pop(0)
                        apply_trace_action_to_environment(self.environment_manager, trace_step)
                        
                        # Update live metrics during playback
                        if trace_step["action"] == "MAKE_VISITED":
                            self.metrics_data["visited_count"] += 1
                        elif trace_step["action"] == "MAKE_PATH":
                            self.metrics_data["path_cost"] += 1
                            # If we draw a path, it's a success
                            self.metrics_data["success"] = True
                else:
                    # Trace is finished playing, shift to RESULT state
                    self.current_app_state = APP_STATE_RESULT

            # EVENT HANDLING PHASE
            for current_event in pygame.event.get():
                if current_event.type == pygame.QUIT:
                    application_is_running = False
                    pygame.quit()
                    sys.exit()

                # ONLY process mouse clicks if the app is IDLE
                if self.current_app_state == APP_STATE_IDLE:
                    if pygame.mouse.get_pressed()[0]: # Left Click
                        pos = pygame.mouse.get_pos()
                        if pos[0] < self.grid_pixel_dimension:
                            row, col = translate_mouse_position_to_grid_indices(pos, self.total_row_count, self.total_column_count, self.grid_pixel_dimension)
                            self.environment_manager.handle_manual_node_placement(row, col)

                    elif pygame.mouse.get_pressed()[2]: # Right Click
                        pos = pygame.mouse.get_pos()
                        if pos[0] < self.grid_pixel_dimension:
                            row, col = translate_mouse_position_to_grid_indices(pos, self.total_row_count, self.total_column_count, self.grid_pixel_dimension)
                            self.environment_manager.handle_manual_node_removal(row, col)

                # Keyboard Inputs
                if current_event.type == pygame.KEYDOWN:
                    # Clear Grid (Allowed in IDLE and RESULT states)
                    if current_event.key == pygame.K_c and self.current_app_state != APP_STATE_RUNNING:
                        self.environment_manager.reset_environment_state()
                        self.current_app_state = APP_STATE_IDLE
                        self.metrics_data = {"visited_count": 0, "path_cost": 0, "execution_time": 0.0}
                        self.active_execution_trace = []
                    
                    # Generate Maze (Allowed in IDLE and RESULT states)
                    if current_event.key == pygame.K_g and self.current_app_state != APP_STATE_RUNNING:
                        self.environment_manager.reset_environment_state()
                        self.environment_manager.generate_random_maze(obstacle_density=0.3)
                        self.current_app_state = APP_STATE_IDLE

                    # Switch Configurations (Allowed ONLY in IDLE state)
                    if self.current_app_state == APP_STATE_IDLE:
                        if current_event.key == pygame.K_a:
                            self.current_algo_index = (self.current_algo_index + 1) % len(self.algorithm_names)
                        
                        if current_event.key == pygame.K_h:
                            self.current_heur_index = (self.current_heur_index + 1) % len(self.heuristic_names)

                        if current_event.key == pygame.K_SPACE:
                            if self.environment_manager.agent_start_node and self.environment_manager.navigation_goal_node:
                                algo_func = self.available_algorithms[active_algo_name]
                                heur_func = self.available_heuristics[active_heur_name]
                                
                                start_time = time.perf_counter()
                                self.active_execution_trace = algo_func(self.environment_manager, heur_func)
                                end_time = time.perf_counter()
                                
                                # Reset all metrics for the new run
                                self.metrics_data["execution_time"] = (end_time - start_time) * 1000
                                self.metrics_data["visited_count"] = 0
                                self.metrics_data["path_cost"] = 0
                                # Start as False 
                                self.metrics_data["success"] = False 
                                
                                self.current_app_state = APP_STATE_RUNNING

            clock.tick(60) # Lock the application to 60 FPS

def execute_visualizer():
    main_application_instance = PathfindingVisualizerApp()
    main_application_instance.run_application_loop()
