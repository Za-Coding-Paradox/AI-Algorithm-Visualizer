from queue import PriorityQueue

def execute_greedy_best_first_search(environment_manager, heuristic_function):
    """
    Requirement: Greedy Best-First Search (GBFS).
    Uses ONLY the heuristic evaluation f(n) = h(n).
    """
    start_node = environment_manager.agent_start_node
    goal_node = environment_manager.navigation_goal_node
    
    if not start_node or not goal_node:
        return []

    # Local import or reuse from a shared utility file
    from algorithms.a_star import reset_algorithmic_data
    reset_algorithmic_data(environment_manager)
    
    execution_trace = []
    tie_breaker_counter = 0 
    # using this as a counter to track which node came first (if two, or more nodes have same priority), or more.
    # tie_breaker basically acts as the ticked id, for two vip customers.
    open_evaluation_queue = PriorityQueue()
    
    # f(n) = h(n)
    start_node.total_estimated_search_cost = heuristic_function(start_node, goal_node)
    open_evaluation_queue.put((start_node.total_estimated_search_cost, tie_breaker_counter, start_node))
    
    nodes_in_queue_hash = {start_node}
    visited_nodes_set = set() # Critical for GBFS to prevent infinite loops

    while not open_evaluation_queue.empty():
        current_evaluating_node = open_evaluation_queue.get()[2]
        nodes_in_queue_hash.remove(current_evaluating_node)
        visited_nodes_set.add(current_evaluating_node)

        # Goal Check
        if current_evaluating_node == goal_node:
            path_trace = []
            while current_evaluating_node.previous_traversal_node is not None:
                current_evaluating_node = current_evaluating_node.previous_traversal_node
                if current_evaluating_node != start_node:
                    path_trace.append({
                        "action": "MAKE_PATH",
                        "node_coords": current_evaluating_node.get_grid_coordinates()
                    })
            path_trace.reverse()
            execution_trace.extend(path_trace)
            return execution_trace

        # Mark Visited
        if current_evaluating_node != start_node:
            execution_trace.append({
                "action": "MAKE_VISITED",
                "node_coords": current_evaluating_node.get_grid_coordinates()
            })

        # Evaluate Neighbors
        current_evaluating_node.identify_walkable_neighbors(environment_manager.grid_matrix)
        
        for neighbor_node in current_evaluating_node.accessible_neighbors:
            if neighbor_node in visited_nodes_set:
                continue

            if neighbor_node not in nodes_in_queue_hash:
                neighbor_node.previous_traversal_node = current_evaluating_node
                
                # f(n) = h(n) ONLY. We do NOT add the movement_cost_weight here.
                neighbor_node.total_estimated_search_cost = heuristic_function(neighbor_node, goal_node)
                
                tie_breaker_counter += 1
                open_evaluation_queue.put((neighbor_node.total_estimated_search_cost, tie_breaker_counter, neighbor_node))
                nodes_in_queue_hash.add(neighbor_node)
                
                if neighbor_node != goal_node:
                    execution_trace.append({
                        "action": "MAKE_FRONTIER",
                        "node_coords": neighbor_node.get_grid_coordinates()
                    })

    return execution_trace
