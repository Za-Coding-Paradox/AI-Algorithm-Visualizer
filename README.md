# AI Pathfinding Visualizer

An interactive, real-time visualization tool for classical AI search algorithms built with Python and Pygame. Place obstacles, set start and goal nodes, generate random mazes, and watch A\* or Greedy Best-First Search navigate the grid — step by step.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Algorithms](#algorithms)
- [Heuristics](#heuristics)
- [Grid & Terrain Weights](#grid--terrain-weights)
- [Controls Reference](#controls-reference)
- [Architecture](#architecture)
- [Configuration](#configuration)

---

## Overview

This project visualizes how informed search algorithms explore a weighted grid environment to find an optimal (or near-optimal) path between a start node and a goal node. Each cell on the grid carries a randomized terrain weight (1–9), making the environment non-uniform and highlighting differences in algorithm behavior.

The application runs as a state machine with three distinct phases — **IDLE**, **RUNNING**, and **RESULT** — giving users clear feedback at every stage of the search process.

---

## Features

- **Real-time step-by-step visualization** of frontier expansion and path reconstruction
- **Two search algorithms**: A\* Search and Greedy Best-First Search
- **Two heuristics**: Manhattan Distance and Euclidean Distance, switchable on the fly
- **Weighted terrain**: Every node carries a movement cost (1–9), affecting A\* path selection
- **Interactive map editor**: Left-click to place start, goal, and wall nodes; right-click to erase
- **Procedural maze generation** with configurable obstacle density
- **Live metrics dashboard**: visited node count, path cost, and execution time (ms)
- **Result overlay popup** showing success/failure status and final statistics
- **60 FPS rendering loop** with configurable playback speed
- **Dynamic grid sizing**: adjustable row/column count and pixel dimensions at instantiation

---

## Project Structure

```
.
├── requirements.txt
├── mise.toml
├── pyrightconfig.json
└── src/
    ├── entry/
    │   └── main.py                  # Application entry point
    ├── app/
    │   └── application.py           # Main app loop, state machine, event handling
    ├── algorithms/
    │   ├── a_star.py                # A* Search implementation
    │   ├── greedy_bfs.py            # Greedy Best-First Search implementation
    │   └── heuristics.py            # Manhattan & Euclidean distance functions
    ├── engine/
    │   ├── grid.py                  # GridNode class and grid construction
    │   ├── environment.py           # SimulationEnvironment (grid state manager)
    │   └── trace_manager.py         # Execution trace playback controller
    └── ui/
        ├── constants.py             # Color palette and node-state color mappings
        ├── window.py                # Pygame display window wrapper
        ├── renderer.py              # Frame renderer: grid, sidebar, popups
        ├── grid_ui.py               # Node drawing and grid line rendering
        └── algorithm_ui.py          # Trace action → node state translator
```

---

## Installation

**Prerequisites:** Python 3.10+ and `pip`.

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-pathfinding-visualizer.git
cd ai-pathfinding-visualizer

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python src/entry/main.py
```

> **Note:** If you are using `mise`, the toolchain is already pinned in `mise.toml`. Run `mise install` before step 3.

---

## Usage

1. **Launch** the application with `python src/entry/main.py`.
2. **Place nodes** on the grid using left-click (first click = Start, second = Goal, subsequent clicks = Walls).
3. **Select** your algorithm (`A`) and heuristic (`H`) from the sidebar.
4. **Press Space** to run the search. The visualization plays back automatically.
5. When the search ends, a **result popup** appears with the final metrics.
6. **Press `C`** to clear the grid and start a new scenario, or **`G`** to generate a fresh random maze.

---

## Algorithms

### A\* Search (`a_star.py`)

A\* is an informed, optimal search algorithm that evaluates each node using the combined cost function:

```
f(n) = g(n) + h(n)
```

- **g(n)** — the cumulative movement cost from the start node to node `n`, accounting for each cell's terrain weight.
- **h(n)** — the heuristic estimate of the remaining cost from `n` to the goal.

A\* guarantees finding the **lowest-cost path** when the heuristic is admissible (never overestimates). Because movement costs are weighted (1–9 per cell), A\* will prefer cheaper terrain over shorter raw distances.

### Greedy Best-First Search (`greedy_bfs.py`)

Greedy BFS evaluates nodes using only the heuristic:

```
f(n) = h(n)
```

It always expands whichever open node appears geometrically closest to the goal, ignoring accumulated path cost. This makes it **faster** in practice but **non-optimal** — it may find a path, but not necessarily the cheapest one. A closed set prevents revisiting nodes and guarantees termination.

---

## Heuristics

Both heuristics operate on grid coordinates `(row, col)`.

| Heuristic | Formula | Best For |
|---|---|---|
| **Manhattan Distance** | `\|x₁ − x₂\| + \|y₁ − y₂\|` | 4-directional grids (matches movement model exactly) |
| **Euclidean Distance** | `√((x₁−x₂)² + (y₁−y₂)²)` | Straight-line estimation; slightly optimistic on 4-way grids |

Manhattan Distance is the **admissible and consistent** choice for this grid since movement is restricted to four cardinal directions. Euclidean Distance will never overestimate on a 4-way grid, so A\* remains optimal with either heuristic.

---

## Grid & Terrain Weights

Each `GridNode` is assigned a random **movement cost weight** (integer from 1 to 9) at creation time. This weight is displayed visually in the center of each non-wall cell.

- **A\*** incorporates this weight into `g(n)`, routing around expensive terrain when a cheaper detour exists.
- **Greedy BFS** ignores weights entirely, treating all passable cells as equal.

The visual difference between the two algorithms is most pronounced in maps with varied terrain costs.

---

## Controls Reference

| Key / Action | Effect | Available In |
|---|---|---|
| **Left Click** | Place Start → Goal → Wall | IDLE |
| **Right Click** | Erase node | IDLE |
| **`Space`** | Run selected algorithm | IDLE |
| **`A`** | Cycle algorithm (A\* ↔ Greedy BFS) | IDLE |
| **`H`** | Cycle heuristic (Manhattan ↔ Euclidean) | IDLE |
| **`G`** | Generate random maze (clears first) | IDLE, RESULT |
| **`C`** | Clear grid and reset all metrics | IDLE, RESULT |
| **Window Close** | Quit application | Any |

---

## Architecture

The application is organized around a clean separation of concerns:

**State Machine (`application.py`)** — The core loop runs at 60 FPS and transitions between three states:

- `IDLE` — Accepts user input for grid editing and configuration.
- `RUNNING` — Replays the pre-computed execution trace at a configurable step rate (default: 5 steps/frame).
- `RESULT` — Displays the final metrics popup and waits for a reset command.

**Execution Trace Pattern** — Algorithms do not directly modify node colors. Instead, each algorithm returns a list of `{"action": str, "node_coords": tuple}` dictionaries. The `ExecutionTracePlaybackManager` and `apply_trace_action_to_environment` function then translate these actions into visual node state changes during the RUNNING phase. This fully decouples algorithmic logic from rendering.

**Engine Layer (`engine/`)** — `SimulationEnvironment` owns the grid matrix and all node placement/removal logic. `GridNode` encapsulates per-cell state (color, weight, pathfinding data) and neighbor discovery.

**UI Layer (`ui/`)** — `ModernInformationRenderer` handles all drawing: the grid frame, the metrics sidebar, and the result overlay. `ApplicationDisplayWindow` wraps the raw Pygame surface.

---

## Configuration

Key parameters are set at instantiation in `application.py` and can be adjusted directly:

| Parameter | Default | Description |
|---|---|---|
| `total_row_count` | `40` | Number of grid rows |
| `total_column_count` | `40` | Number of grid columns |
| `grid_pixel_dimension` | `800` | Pixel width/height of the grid area |
| `sidebar_pixel_dimension` | `300` | Pixel width of the metrics sidebar |
| `steps_per_frame` | `5` | Trace steps rendered per frame (higher = faster playback) |
| `obstacle_density` | `0.3` | Fraction of cells set as walls during maze generation |

To change grid size or window dimensions, modify the `PathfindingVisualizerApp()` constructor call inside `application.py` or pass arguments directly from `main.py`.

---

## License

This project is released under the MIT License. See `LICENSE` for details.
