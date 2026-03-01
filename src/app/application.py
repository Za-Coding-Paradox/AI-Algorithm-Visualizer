import pygame
import sys
import time

from engine.environment import SimulationEnvironment
from ui.window import ApplicationDisplayWindow
from ui.renderer import ModernInformationRenderer
from ui.algorithm_ui import apply_trace_action_to_environment
from engine.dynamic_management import DynamicObstacleManager

from algorithms.a_star import execute_a_star_search
from algorithms.greedy_bfs import execute_greedy_best_first_search
from algorithms.heuristics import calculate_manhattan_distance, calculate_euclidean_distance

# Application States Constants
APP_STATE_IDLE = "IDLE"
APP_STATE_RUNNING = "RUNNING"
APP_STATE_TRANSIT = "TRANSIT"
APP_STATE_RESULT = "RESULT"

def translate_mouse_position_to_grid_indices(mouse_pixel_position, row_limit, column_limit, grid_pixel_width):
    """Accurately maps Pygame (X, Y) to the Grid's (Row, Column) system."""
    node_pixel_gap = grid_pixel_width // max(row_limit, column_limit)
    target_row_index = mouse_pixel_position[0] // node_pixel_gap
    target_column_index = mouse_pixel_position[1] // node_pixel_gap
    return int(target_row_index), int(target_column_index)

class PathfindingVisualizerApp:
    def __init__(self, total_row_count=40, total_column_count=40, grid_pixel_dimension=800, sidebar_pixel_dimension=320):
        pygame.init()
        self.total_row_count = total_row_count
        self.total_column_count = total_column_count
        self.grid_pixel_dimension = grid_pixel_dimension
        
        self.display_window = ApplicationDisplayWindow(
            grid_pixel_dimension + sidebar_pixel_dimension, grid_pixel_dimension, "AI Pathfinding Visualizer"
        )
        self.environment_manager = SimulationEnvironment(total_row_count, total_column_count, grid_pixel_dimension)
        self.information_renderer = ModernInformationRenderer(grid_pixel_dimension, grid_pixel_dimension, sidebar_pixel_dimension)
        
        self.current_app_state = APP_STATE_IDLE
        
        # Algorithm Configurations
        self.available_algorithms = {"A* Search": execute_a_star_search, "Greedy BFS": execute_greedy_best_first_search}
        self.available_heuristics = {"Manhattan": calculate_manhattan_distance, "Euclidean": calculate_euclidean_distance}
        self.algorithm_names = list(self.available_algorithms.keys())
        self.heuristic_names = list(self.available_heuristics.keys())
        self.current_algo_index = 0
        self.current_heur_index = 0
        
        # Trace & Metrics
        self.active_execution_trace = []
        self.metrics_data = {"visited_count": 0, "path_cost": 0, "execution_time": 0.0, "success": False}
        
        # Dynamic Mode & Agent Variables
        self.dynamic_mode_enabled = False
        self.agent_coords = None
        self.remaining_path = []
        self.transit_timer = 0

    def run_application_loop(self):
        application_is_running = True
        clock = pygame.time.Clock()

        while application_is_running:
            target_display_surface = self.display_window.get_main_surface()
            
            # Pass dynamic mode status to the renderer and draw base environment
            self.information_renderer.dynamic_mode = self.dynamic_mode_enabled
            self.information_renderer.render_complete_environment_frame(
                target_display_surface, self.environment_manager, self.agent_coords
            )
            
            active_algo_name = self.algorithm_names[self.current_algo_index]
            active_heur_name = self.heuristic_names[self.current_heur_index]
            
            # Draw Sidebar Dashboard
            self.information_renderer.draw_metrics_dashboard(
                target_display_surface, self.current_app_state, 
                active_algo_name, active_heur_name, self.metrics_data
            )
            
            # Draw Pop-up Overlay if finished
            if self.current_app_state == APP_STATE_RESULT:
                self.information_renderer.draw_result_popup_overlay(target_display_surface, self.metrics_data)

            self.display_window.refresh_display_state()

            # --- RUNNING STATE (Search Animation) ---
            if self.current_app_state == APP_STATE_RUNNING:
                if len(self.active_execution_trace) > 0:
                    steps_per_frame = 5 
                    for _ in range(min(steps_per_frame, len(self.active_execution_trace))):
                        trace_step = self.active_execution_trace.pop(0)
                        apply_trace_action_to_environment(self.environment_manager, trace_step)
                        
                        # Live Metric Updates
                        if trace_step["action"] == "MAKE_VISITED":
                            self.metrics_data["visited_count"] += 1
                        elif trace_step["action"] == "MAKE_PATH":
                            self.metrics_data["path_cost"] += 1
                            self.metrics_data["success"] = True # Bulletproof success assignment
                else:
                    # Trace finished playing. Move agent or show results.
                    if self.metrics_data["success"]:
                        self.current_app_state = APP_STATE_TRANSIT
                        self.agent_coords = self.environment_manager.agent_start_node.get_grid_coordinates()
                    else:
                        self.current_app_state = APP_STATE_RESULT

            # --- TRANSIT STATE (Dynamic Obstacles & Agent Movement) ---
            elif self.current_app_state == APP_STATE_TRANSIT:
                self.transit_timer += 1
                
                # Move agent every 8 frames for smooth visual pacing
                if self.transit_timer > 8:
                    self.transit_timer = 0
                    if len(self.remaining_path) > 0:
                        self.agent_coords = self.remaining_path.pop(0)
                    else:
                        self.current_app_state = APP_STATE_RESULT # Reached goal
                        
                    # Dynamic Spawning & Re-planning Logic
                    if self.dynamic_mode_enabled:
                        spawned_coords = DynamicObstacleManager.attempt_spawn_obstacle(self.environment_manager)
                        
                        # Only recalculate if the obstacle landed precisely on our green path
                        if spawned_coords and DynamicObstacleManager.is_collision_on_path(spawned_coords, self.remaining_path):
                            
                            algo_func = self.available_algorithms[active_algo_name]
                            heur_func = self.available_heuristics[active_heur_name]
                            
                            # Trigger replanning from current location
                            self.active_execution_trace = DynamicObstacleManager.trigger_replanning(
                                self.environment_manager, self.agent_coords, algo_func, heur_func
                            )
                            
                            # Grab new path coords for the agent to follow
                            self.remaining_path = [step["node_coords"] for step in self.active_execution_trace if step["action"] == "MAKE_PATH"]
                            self.metrics_data["success"] = False # Reset flag while it re-animates
                            self.current_app_state = APP_STATE_RUNNING # Animate the new search

            # --- INPUT HANDLING ---
            for current_event in pygame.event.get():
                if current_event.type == pygame.QUIT:
                    application_is_running = False
                    pygame.quit()
                    sys.exit()

                # Mouse interaction ONLY permitted in IDLE state
                if self.current_app_state == APP_STATE_IDLE:
                    if pygame.mouse.get_pressed()[0]:
                        pos = pygame.mouse.get_pos()
                        if pos[0] < self.grid_pixel_dimension:
                            row, col = translate_mouse_position_to_grid_indices(pos, self.total_row_count, self.total_column_count, self.grid_pixel_dimension)
                            self.environment_manager.handle_manual_node_placement(row, col)

                    elif pygame.mouse.get_pressed()[2]:
                        pos = pygame.mouse.get_pos()
                        if pos[0] < self.grid_pixel_dimension:
                            row, col = translate_mouse_position_to_grid_indices(pos, self.total_row_count, self.total_column_count, self.grid_pixel_dimension)
                            self.environment_manager.handle_manual_node_removal(row, col)

                # Keyboard Commands
                if current_event.type == pygame.KEYDOWN:
                    
                    # Clear Grid (Allowed in IDLE and RESULT states)
                    if current_event.key == pygame.K_c and self.current_app_state != APP_STATE_RUNNING:
                        self.environment_manager.reset_environment_state()
                        self.current_app_state = APP_STATE_IDLE
                        self.metrics_data = {"visited_count": 0, "path_cost": 0, "execution_time": 0.0, "success": False}
                        self.active_execution_trace = []
                        self.agent_coords = None
                        self.remaining_path = []
                    
                    # Generate Maze (Allowed in IDLE and RESULT states)
                    if current_event.key == pygame.K_g and self.current_app_state != APP_STATE_RUNNING:
                        self.environment_manager.reset_environment_state()
                        self.environment_manager.generate_random_maze(obstacle_density=0.3)
                        self.current_app_state = APP_STATE_IDLE
                        self.agent_coords = None
                        self.remaining_path = []

                    # Configuration Switches (Allowed ONLY in IDLE state)
                    if self.current_app_state == APP_STATE_IDLE:
                        if current_event.key == pygame.K_a:
                            self.current_algo_index = (self.current_algo_index + 1) % len(self.algorithm_names)
                        
                        if current_event.key == pygame.K_h:
                            self.current_heur_index = (self.current_heur_index + 1) % len(self.heuristic_names)
                            
                        if current_event.key == pygame.K_d:
                            self.dynamic_mode_enabled = not self.dynamic_mode_enabled

                        # START SEARCH
                        if current_event.key == pygame.K_SPACE:
                            if self.environment_manager.agent_start_node and self.environment_manager.navigation_goal_node:
                                algo_func = self.available_algorithms[active_algo_name]
                                heur_func = self.available_heuristics[active_heur_name]
                                
                                # Measure pure math calculation time
                                start_time = time.perf_counter()
                                self.active_execution_trace = algo_func(self.environment_manager, heur_func)
                                end_time = time.perf_counter()
                                
                                # Pre-extract the physical coordinates for the agent to follow later
                                self.remaining_path = [step["node_coords"] for step in self.active_execution_trace if step["action"] == "MAKE_PATH"]
                                
                                self.metrics_data["execution_time"] = (end_time - start_time) * 1000
                                self.metrics_data["visited_count"] = 0
                                self.metrics_data["path_cost"] = 0
                                self.metrics_data["success"] = False 
                                
                                self.current_app_state = APP_STATE_RUNNING

            clock.tick(60)

def execute_visualizer():
    main_application_instance = PathfindingVisualizerApp()
    main_application_instance.run_application_loop()
