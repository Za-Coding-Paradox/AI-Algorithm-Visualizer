def apply_trace_action_to_environment(environment_manager, trace_step):
    """Translates algorithmic string actions into physical node state updates."""

    action_type = trace_step["action"]
    row, column = trace_step["node_coords"]
    target_node = environment_manager.grid_matrix[row][column]
    
    if action_type == "MAKE_VISITED":
        target_node.set_as_explored_node()

    elif action_type == "MAKE_FRONTIER":
        target_node.set_as_frontier_node()

    elif action_type == "MAKE_PATH":
        target_node.set_as_final_path_segment()
