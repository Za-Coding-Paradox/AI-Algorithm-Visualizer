import pygame
import sys
from ui.algorithm_ui import apply_trace_action_to_environment

class ExecutionTracePlaybackManager:
    def __init__(self, playback_delay_milliseconds=15):
        """
        Manages the playback speed and execution of algorithm traces.
        A lower delay means faster visualization.
        """
        self.playback_delay_milliseconds = playback_delay_milliseconds

    def execute_playback_sequence(
        self, 
        execution_trace, 
        environment_manager, 
        information_renderer, 
        display_window
    ):
        """
        Iterates through the generated algorithm steps, updates the UI, 
        and manages the visual delay without freezing the application.
        """
        target_display_surface = display_window.get_main_surface()
        
        for trace_step in execution_trace:
            # Prevent the OS from thinking the window is "Not Responding"
            # Allows the user to close the window mid-algorithm
            for current_event in pygame.event.get():
                if current_event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Update the specific node's state using the UI translator
            apply_trace_action_to_environment(environment_manager, trace_step)
            
            # Ask the renderer to draw the newly updated grid
            information_renderer.render_complete_environment_frame(
                target_display_surface, 
                environment_manager
            )
            
            # Push the new frame to the monitor
            display_window.refresh_display_state()
            
            # Apply the delay to create the animation effect
            pygame.time.delay(self.playback_delay_milliseconds)
