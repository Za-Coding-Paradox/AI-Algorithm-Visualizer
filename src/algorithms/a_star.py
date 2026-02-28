from queue import PriorityQueue

def reset_algorithmic_data(environment_manager):
    for grid_row in environment_manager.grid_matrix:
        for individual_node in grid_row:
            individual_node.cost_from_start_node = float("inf")
            individual_node.total_estimated_search_cost = float("inf")
            individual_node.previous_traversal_node = None

def execute_a_star_search(environment_manager, heuristic_function):
    """
    Requirement: A* Search.
    Uses the combined evaluation function f(n) = g(n) + h(n).
    """
    start_node = environment_manager.agent_start_node
    goal_node = environment_manager.navigation_goal_node
    
    if not start_node or not goal_node:
        return []

    reset_algorithmic_data(environment_manager)
    execution_trace = []
    
    tie_breaker_counter = 0
    open_evaluation_queue = PriorityQueue()
    
    # Initialize Start Node
    start_node.cost_from_start_node = 0
    start_node.total_estimated_search_cost = heuristic_function(start_node, goal_node)
    open_evaluation_queue.put((start_node.total_estimated_search_cost, tie_breaker_counter, start_node))
    
    nodes_in_queue_hash = {start_node}

    while not open_evaluation_queue.empty():
        current_evaluating_node = open_evaluation_queue.get()[2]
        nodes_in_queue_hash.remove(current_evaluating_node)

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

        # Mark Visited (for the visualizer)
        if current_evaluating_node != start_node:
            execution_trace.append({
                "action": "MAKE_VISITED",
                "node_coords": current_evaluating_node.get_grid_coordinates()
            })

        # Evaluate Neighbors
        current_evaluating_node.identify_walkable_neighbors(environment_manager.grid_matrix)
        
        for neighbor_node in current_evaluating_node.accessible_neighbors:
            
            # g(n): Current path cost + the specific weight of moving to this neighbor
            tentative_cost_from_start = current_evaluating_node.cost_from_start_node + neighbor_node.movement_cost_weight

            if tentative_cost_from_start < neighbor_node.cost_from_start_node:
                neighbor_node.previous_traversal_node = current_evaluating_node
                neighbor_node.cost_from_start_node = tentative_cost_from_start
                
                # h(n): Heuristic estimate to the goal
                heuristic_cost_to_goal = heuristic_function(neighbor_node, goal_node)
                
                # f(n) = g(n) + h(n)
                neighbor_node.total_estimated_search_cost = tentative_cost_from_start + heuristic_cost_to_goal
                
                if neighbor_node not in nodes_in_queue_hash:
                    tie_breaker_counter += 1
                    open_evaluation_queue.put((neighbor_node.total_estimated_search_cost, tie_breaker_counter, neighbor_node))
                    nodes_in_queue_hash.add(neighbor_node)
                    
                    if neighbor_node != goal_node:
                        execution_trace.append({
                            "action": "MAKE_FRONTIER",
                            "node_coords": neighbor_node.get_grid_coordinates()
                        })

    return execution_trace
