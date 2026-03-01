# AI Pathfinding Visualizer

A real-time, interactive pathfinding visualization engine built with Python and Pygame. Supports weighted terrain grids, two informed search algorithms, two admissible heuristics, animated agent traversal, and a **dynamic obstacle system** with live path replanning — all rendered at 60 FPS through a clean state machine architecture.

---

## Table of Contents

- [Overview](#overview)
- [Feature Set](#feature-set)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [State Machine](#state-machine)
- [Algorithms](#algorithms)
- [Heuristics](#heuristics)
- [Dynamic Obstacle System](#dynamic-obstacle-system)
- [Grid & Terrain Weights](#grid--terrain-weights)
- [Execution Trace Pattern](#execution-trace-pattern)
- [Controls Reference](#controls-reference)
- [Architecture Deep-Dive](#architecture-deep-dive)
- [Configuration](#configuration)
- [Color Legend](#color-legend)

---

## Overview

This visualizer simulates an intelligent agent navigating a weighted grid from a user-defined start node to a goal node. Beyond simple pathfinding, it models **dynamic environments**: once the agent begins traversing the computed path, new obstacles can spawn probabilistically at every time step. If a spawned obstacle lands on the agent's remaining route, the system immediately triggers a full replan from the agent's current position — visualizing the entire new search before resuming movement.

The project demonstrates four tightly integrated concepts: informed search, admissible heuristics, weighted cost traversal, and reactive replanning in non-stationary environments.

---

## Feature Set

**Search & Heuristics**
- A\* Search with full `g(n) + h(n)` cost accounting across weighted terrain
- Greedy Best-First Search with `h(n)`-only evaluation for speed comparison
- Manhattan Distance heuristic (admissible and consistent for 4-directional grids)
- Euclidean Distance heuristic (admissible but not consistent on 4-way grids)

**Visualization**
- Step-by-step frontier expansion and path reconstruction animation
- Animated agent traversal along the computed path (distinct from the search visualization)
- Live metrics dashboard: visited node count, path cost, and algorithm compute time
- Result overlay popup with success/failure status and final statistics
- Per-cell terrain weight labels displayed on every non-wall node

**Dynamic Environment**
- Toggleable dynamic obstacle mode (`D` key)
- Probabilistic obstacle spawning (3% per agent step, configurable)
- Collision detection: replanning only triggers when a new wall intersects the remaining path
- Full visual re-animation of the replanned search before agent movement resumes

**Map Editing**
- Interactive left-click placement: Start → Goal → Walls, in sequence
- Right-click erasure of any node type
- Procedural maze generation with configurable obstacle density
- Full grid reset preserving window dimensions

---

## Project Structure

```
.
├── requirements.txt
├── mise.toml
├── pyrightconfig.json
└── src/
    ├── entry/
    │   └── main.py                      # Entry point
    │
    ├── app/
    │   └── application.py               # State machine, main loop, event handling
    │
    ├── algorithms/
    │   ├── a_star.py                    # A* Search — f(n) = g(n) + h(n)
    │   ├── greedy_bfs.py                # Greedy BFS — f(n) = h(n)
    │   └── heuristics.py                # Manhattan & Euclidean distance functions
    │
    ├── engine/
    │   ├── grid.py                      # GridNode class, per-cell state & neighbor discovery
    │   ├── environment.py               # SimulationEnvironment — grid ownership & map ops
    │   ├── dynamic_management.py        # DynamicObstacleManager — spawn, detect, replan
    │   └── trace_manager.py             # ExecutionTracePlaybackManager (frame-delay mode)
    │
    └── ui/
        ├── constants.py                 # Color palette & node-state color constants
        ├── window.py                    # Pygame display surface wrapper
        ├── renderer.py                  # Top-level frame compositor
        ├── grid_ui.py                   # Per-node rectangle & grid line drawing
        ├── dashboard_ui.py              # Sidebar metrics panel & result popup drawing
        └── algorithm_ui.py              # Trace action → node visual state translator
```

---

## Installation

**Prerequisites:** Python 3.10+, `pip`.

```bash
# Clone
git clone https://github.com/your-username/ai-pathfinding-visualizer.git
cd ai-pathfinding-visualizer

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
.venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python src/entry/main.py
```

> If using `mise`, run `mise install` before `pip install` to pin the Python toolchain defined in `mise.toml`.

---

## Usage

1. **Launch** the application. An empty 40×40 weighted grid appears on the left; the metrics sidebar is on the right.
2. **Left-click** a cell to place the **Start node** (orange). Left-click again to place the **Goal node** (teal). All subsequent left-clicks place **wall obstacles** (black).
3. **Right-click** any cell to erase it.
4. Optionally press **`G`** to generate a random maze, or **`D`** to toggle Dynamic Obstacle Mode.
5. Press **`A`** / **`H`** to cycle the active algorithm and heuristic.
6. Press **`Space`** to execute the search. The frontier expansion animates first, then the path is drawn, then the agent (dark blue circle) traverses the path.
7. In Dynamic Mode, obstacles may spawn during agent traversal. If one blocks the path, the search re-runs from the agent's current position and the agent follows the new route.
8. At completion, the **result popup** shows final metrics. Press **`C`** to reset.

---

## State Machine

The application runs as a strict four-state machine. State transitions are deterministic and driven by algorithm completion, trace exhaustion, or user input.

```
                         ┌─────────────────────────────────────┐
                         │               IDLE                  │
                         │  • Mouse editing enabled            │
                         │  • Config switches (A, H, D)        │
                         │  • G: generate maze                 │
                         │  • Space: run algorithm → RUNNING   │
                         └────────────────┬────────────────────┘
                                          │ Space (start + goal set)
                                          ▼
                         ┌─────────────────────────────────────┐
                         │              RUNNING                │
                         │  • Replay execution trace           │
                         │  • 5 steps/frame                    │
                         │  • Updates visited_count,           │
                         │    path_cost, success flag          │
                         │  • Trace empty + success → TRANSIT  │
                         │  • Trace empty + fail   → RESULT    │
                         └────────────────┬────────────────────┘
                                          │ success=True
                                          ▼
                         ┌─────────────────────────────────────┐
                         │             TRANSIT                 │
                         │  • Agent moves 1 step every 8 frames│
                         │  • Dynamic Mode: attempt obstacle   │
                         │    spawn each step                  │
                         │  • Collision on path → RUNNING      │
                         │    (replanned trace)                │
                         │  • Path exhausted → RESULT          │
                         └────────────────┬────────────────────┘
                                          │ path done
                                          ▼
                         ┌─────────────────────────────────────┐
                         │              RESULT                 │
                         │  • Popup overlay rendered           │
                         │  • C: clear → IDLE                  │
                         │  • G: new maze → IDLE               │
                         └─────────────────────────────────────┘
```

---

## Algorithms

### A\* Search — `algorithms/a_star.py`

A\* is a complete, optimal informed search algorithm. It evaluates every open node using:

```
f(n) = g(n) + h(n)
```

- **`g(n)`** — the exact cumulative cost to reach node `n` from the start, summed over each traversed cell's `movement_cost_weight` (an integer 1–9 assigned randomly per node at grid creation).
- **`h(n)`** — the heuristic estimate of the cheapest path from `n` to the goal.

The priority queue always expands the node with the lowest `f(n)`. When the heuristic is **admissible** (never overestimates the true cost), A\* guarantees finding the globally optimal path. With weighted terrain, this means A\* may route around a geometrically shorter path if that path passes through high-cost cells.

Implementation details:
- Uses Python's `PriorityQueue` (heap-backed, O(log n) push/pop).
- A tie-breaker counter prevents the heap from attempting to compare `GridNode` objects when `f(n)` values are equal.
- `nodes_in_queue_hash` (a set) provides O(1) membership tests to avoid redundant queue insertions.
- The open set does not track closed nodes — revisits are prevented implicitly because a better `g(n)` is required to update any node.

### Greedy Best-First Search — `algorithms/greedy_bfs.py`

Greedy BFS uses only the heuristic to rank nodes:

```
f(n) = h(n)
```

It always expands whichever open node appears geometrically closest to the goal, completely ignoring accumulated path cost. This makes it **faster** than A\* in practice — it explores far fewer nodes — but **non-optimal**: the path it finds may be longer or more expensive than necessary.

Implementation details:
- Maintains an explicit `visited_nodes_set` (a closed list). This is **essential** for GBFS: without it, the algorithm can cycle indefinitely in weighted graphs where heuristic values alone do not strictly decrease.
- Does not add `movement_cost_weight` to any evaluation — purely geometric priority.
- Shares the `reset_algorithmic_data` utility from `a_star.py` to clear per-node state before each run.

---

## Heuristics

Both heuristics operate on `(row, column)` grid coordinates returned by `node.get_grid_coordinates()`.

| Heuristic | Formula | Admissible | Consistent |
|---|---|---|---|
| **Manhattan Distance** | `\|r₁−r₂\| + \|c₁−c₂\|` | Yes | Yes |
| **Euclidean Distance** | `√((r₁−r₂)² + (c₁−c₂)²)` | Yes | No (on 4-way grids) |

**Why Manhattan is the correct choice for this grid:**
Movement is restricted to four cardinal directions (up, down, left, right). The true minimum number of steps between two cells is exactly the Manhattan distance. The heuristic never overestimates, making it admissible. It is also consistent — `h(n) ≤ cost(n, n') + h(n')` for every edge — which means A\* never needs to re-open closed nodes.

**Euclidean on a 4-way grid:**
Euclidean distance is always ≤ Manhattan distance in grid space, so it is admissible but not consistent. A\* remains correct with it, but may do slightly more work. The visual difference between the two heuristics is most apparent in open maps: Euclidean tends to produce a narrower, more diagonal-looking explored region despite the grid being 4-directional.

---

## Dynamic Obstacle System

Implemented in `engine/dynamic_management.py` via the `DynamicObstacleManager` static class.

### How It Works

During the `TRANSIT` state, on each agent movement tick (every 8 frames), three operations run in sequence:

**1. Spawn Attempt — `attempt_spawn_obstacle()`**
A random float is drawn. With 3% probability, a random `EMPTY_COLOR` cell in the entire grid is selected and converted to a wall. The coordinates of the new wall are returned, or `None` if no spawn occurred.

```python
if random.random() > spawn_probability:   # 97% of calls return here
    return None
spawned_node = random.choice(empty_nodes)
spawned_node.set_as_static_obstacle()
return spawned_node.get_grid_coordinates()
```

**2. Collision Check — `is_collision_on_path()`**
This is the efficiency gate. The `remaining_path` is a pre-extracted list of `(row, col)` tuples that the agent has not yet walked. If the spawned coordinate is not in that list, the entire replanning step is skipped — no unnecessary recalculation for obstacles that spawn somewhere irrelevant.

```python
return spawned_coords in remaining_path_coords   # O(n) list scan
```

> For grids larger than 1000×1000, this should be a `set` for O(1) lookup. On a 40×40 grid the current list scan is negligible.

**3. Replanning — `trigger_replanning()`**
When a collision is confirmed:
- The environment's `agent_start_node` is **temporarily** reassigned to the agent's current grid cell, making the algorithm believe the search starts from the agent's present location.
- `clear_search_visuals()` wipes all `VISITED`, `FRONTIER`, and `PATH` colored cells from the grid without disturbing walls, start, or goal.
- The selected algorithm runs from scratch and returns a new execution trace.
- The original `agent_start_node` is restored.
- The application transitions back to `RUNNING` to animate the new search, then resumes `TRANSIT` on the updated path.

```
Agent at (12, 8) → obstacle spawns at (15, 8) → (15, 8) in remaining_path
→ agent_start_node = grid[12][8]
→ clear_search_visuals()
→ new_trace = algo_func(environment, heur_func)
→ remaining_path = [coords from new MAKE_PATH steps]
→ state = RUNNING (re-animate new search)
→ state = TRANSIT (resume movement on new path)
```

---

## Grid & Terrain Weights

Each `GridNode` is assigned a `movement_cost_weight` — a random integer from 1 to 9 — at construction time. This value is:

- **Displayed** as a number in the center of each non-wall cell.
- **Used by A\*** as the cost of entering that cell: `g(neighbor) = g(current) + neighbor.movement_cost_weight`.
- **Ignored by Greedy BFS**, which treats all passable cells as equal.

The terrain weight system means A\* will sometimes take a geometrically longer route if it passes through cheaper cells. The visual contrast between A\* and Greedy BFS is most dramatic in maps with clustered high-cost terrain: Greedy BFS charges through it, A\* routes around it.

Path cost reported in the metrics dashboard is the **count of path nodes visualized**, not the weighted sum. The weighted `g(n)` value is internal to the algorithm; the reported metric reflects path length for visual clarity.

---

## Execution Trace Pattern

Algorithms in this system are **fully decoupled from the renderer**. Neither `execute_a_star_search` nor `execute_greedy_best_first_search` calls any Pygame function or directly mutates node colors. Instead, each returns a list of action dictionaries:

```python
[
    {"action": "MAKE_FRONTIER", "node_coords": (3, 7)},
    {"action": "MAKE_VISITED",  "node_coords": (2, 7)},
    {"action": "MAKE_PATH",     "node_coords": (2, 7)},
    ...
]
```

The `apply_trace_action_to_environment()` function in `algorithm_ui.py` consumes these actions during the `RUNNING` state, translating each string action into the appropriate `GridNode` color-setter method.

**Why this matters:**
- Algorithms can be unit-tested independently with no Pygame dependency.
- Playback speed (steps per frame) is controlled entirely in the application loop, not inside the algorithm.
- The same trace can be replayed, inspected, or exported without re-running the search.
- Dynamic replanning reuses the same trace mechanism — a replanned search produces a new trace that feeds back into the same `RUNNING` state handler.

---

## Controls Reference

| Input | Action | Available In |
|---|---|---|
| **Left Click** (grid) | Place Start → Goal → Wall | IDLE |
| **Right Click** (grid) | Erase node | IDLE |
| **`Space`** | Execute selected algorithm | IDLE |
| **`A`** | Cycle algorithm (A\* ↔ Greedy BFS) | IDLE |
| **`H`** | Cycle heuristic (Manhattan ↔ Euclidean) | IDLE |
| **`D`** | Toggle Dynamic Obstacle Mode | IDLE |
| **`G`** | Generate random maze (resets grid first) | IDLE, RESULT |
| **`C`** | Clear grid, reset all state and metrics | IDLE, RESULT |
| **Close Window** | Quit application | Any |

---

## Architecture Deep-Dive

### Layer Separation

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Point                          │
│              src/entry/main.py                          │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│               Application Layer (app/)                  │
│  PathfindingVisualizerApp                               │
│  • 60 FPS game loop                                     │
│  • State machine (IDLE → RUNNING → TRANSIT → RESULT)    │
│  • Input routing                                        │
│  • Owns: environment_manager, information_renderer,     │
│          active_execution_trace, remaining_path,        │
│          agent_coords, metrics_data                     │
└───────────┬─────────────────────────┬───────────────────┘
            │                         │
┌───────────▼───────────┐   ┌─────────▼─────────────────┐
│    Engine Layer       │   │      UI Layer              │
│    (engine/)          │   │      (ui/)                 │
│                       │   │                            │
│  SimulationEnvironment│   │  ModernInformationRenderer │
│  • Owns grid_matrix   │   │  • render_complete_frame() │
│  • Node placement     │   │  • draw_metrics_dashboard()│
│  • clear_search_vis() │   │  • draw_result_popup()     │
│                       │   │                            │
│  GridNode             │   │  dashboard_ui.py           │
│  • Color state        │   │  • Sidebar layout & fonts  │
│  • movement_cost      │   │  • Popup geometry          │
│  • neighbor discovery │   │                            │
│                       │   │  grid_ui.py                │
│  DynamicObstacleManager   │  • Node rectangle drawing  │
│  • spawn / detect /   │   │  • Grid line drawing       │
│    replan             │   │  • Weight text rendering   │
│                       │   │                            │
│  algorithms/          │   │  algorithm_ui.py           │
│  • a_star.py          │   │  • Trace action → setState │
│  • greedy_bfs.py      │   │                            │
│  • heuristics.py      │   │  window.py                 │
│                       │   │  • Pygame surface wrapper  │
└───────────────────────┘   └────────────────────────────┘
```

### Key Design Decisions

**`renderer.py` as a thin compositor:** `ModernInformationRenderer` does not contain any drawing logic itself. It holds fonts and color constants, then delegates all actual rendering calls to `grid_ui.py` and `dashboard_ui.py`. This makes each drawing subsystem independently testable and replaceable.

**Pre-extracted `remaining_path`:** When the algorithm trace is computed at search time, the application immediately extracts all `MAKE_PATH` step coordinates into a separate `remaining_path` list. This list is what the agent follows during `TRANSIT` and what `DynamicObstacleManager` checks for collisions — the execution trace itself is consumed during `RUNNING` and would be empty by the time the agent moves.

**`agent_coords` as a rendering overlay:** The agent (dark blue circle) is drawn as an overlay on top of the existing grid state, not as a node color modification. This preserves the green path visualization underneath the agent as it moves.

---

## Configuration

All primary parameters are set in `PathfindingVisualizerApp.__init__()`:

| Parameter | Default | Description |
|---|---|---|
| `total_row_count` | `40` | Grid row count |
| `total_column_count` | `40` | Grid column count |
| `grid_pixel_dimension` | `800` | Pixel width and height of the grid area |
| `sidebar_pixel_dimension` | `320` | Pixel width of the metrics sidebar |
| `steps_per_frame` | `5` | Trace steps consumed per frame during RUNNING |
| `transit_timer` threshold | `8` | Frames between each agent movement step |
| `obstacle_density` | `0.3` | Fraction of cells walled during maze generation |
| `spawn_probability` | `0.03` | Per-step probability of a dynamic obstacle spawning |

To modify spawn probability or agent movement speed, adjust `attempt_spawn_obstacle(spawn_probability=...)` in `application.py` and the `transit_timer > 8` threshold respectively.

---

## Color Legend

| Color | Node State |
|---|---|
| White | Empty (traversable) |
| Orange | Agent start position |
| Teal / Turquoise | Navigation goal |
| Black | Wall / obstacle |
| Yellow | Frontier (open set, discovered but not expanded) |
| Red | Visited (closed set, fully expanded) |
| Green | Final path |
| Dark Blue Circle | Agent in transit (rendered as overlay) |

---

## License

Released under the MIT License. See `LICENSE` for details.
