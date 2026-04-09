*This project has been created as part of the 42 curriculum by aluslu.*

# Fly-in

## Description

Fly-in is a drone-routing simulation project.
It reads a map file, validates it, computes collision-aware schedules for multiple
drones, prints turn-by-turn movement logs, and displays the simulation in a
Pygame window.

The main goal is to route all drones from a start hub to an end hub while
respecting traffic constraints:

- Hub capacity (`max_drones`)
- Link capacity (`max_link_capacity`)
- Zone behavior (`normal`, `priority`, `restricted`, `blocked`)

The project focuses on pathfinding under constraints, with attention to
readability, validation robustness, and a useful visual interface for analyzing
the solution.

## Instructions

### Prerequisites

- Python 3.10+
- `uv` installed (recommended workflow used by the project)

### Installation

```bash
make install
```

This installs all runtime and development dependencies declared in
`pyproject.toml`.

### Run the simulation

```bash
make run ARGS=maps/easy/01_linear_path.txt
```

Equivalent command:

```bash
uv run python -m src maps/easy/01_linear_path.txt
```

### Debug mode

```bash
make debug ARGS=maps/easy/01_linear_path.txt
```

### Quality checks

```bash
make lint
```

## Map File Format

Map files are plain `.txt` files with one declaration per line:

- `nb_drones: <positive_int>`
- `start_hub: <name> <x> <y> [optional_metadata]`
- `hub: <name> <x> <y> [optional_metadata]`
- `end_hub: <name> <x> <y> [optional_metadata]`
- `connection: <hub_a>-<hub_b> [optional_metadata]`

Supported metadata:

- Hub metadata: `[zone=<normal|priority|restricted|blocked> color=<name> max_drones=<int>]`
- Connection metadata: `[max_link_capacity=<int>]`

Important parser rules:

- The first non-empty/non-comment key must be `nb_drones`.
- Hubs must be declared before connections that reference them.
- Start and end hubs must exist exactly once.
- Hub names and coordinates must be unique.
- Duplicate connections are rejected.
- Start and end hubs must not be isolated.
- Comments (`# ...`) and blank lines are ignored.

Minimal example:

```txt
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
end_hub: goal 2 0 [color=red]

connection: start-waypoint1
connection: waypoint1-goal
```

## Algorithm Choices And Implementation Strategy

### 1. Parsing and validation strategy

The parser is line-oriented and routes each key to a dedicated handler.
Validation is split into two layers:

- Structural line-level checks in the parser.
- Field-level checks with Pydantic models (`Hub`, `Connection`, metadata).

This separation keeps errors explicit and easier to diagnose.

### 2. Heuristic precomputation (reverse Dijkstra)

Before planning any drone path, the router computes estimated remaining cost from
every hub to the destination using a reverse Dijkstra pass.

- `blocked` hubs are ignored.
- Entering `restricted` areas is modeled as more expensive.

These distances are reused as the heuristic component for A* to reduce search
work.

### 3. Path search (A* on space-time states)

Each search node stores:

- Current hub name
- Turns elapsed from start
- Estimated total turns (`g + h`)
- Parent pointer for path reconstruction

The state space is time-aware (`turn`, `hub`) so the algorithm can model waiting
and avoid temporal conflicts.

### 4. Conflict and capacity management (reservation table)

A central reservation table stores occupancy of hubs and links per turn.

- Hubs: `(turn, hub_name) -> number_of_drones`
- Links: `(turn, connection_name) -> number_of_drones`

When exploring neighbors, a move is accepted only if capacities are respected.
Two move models are used:

- Normal/Priority destination: 1 turn
- Restricted destination: 2 turns (link occupancy reserved for both turns)

The planner also includes a wait action to resolve bottlenecks safely.

### 5. Multi-drone scheduling approach

Drones are planned sequentially.
After each path is found, reservations are updated, so the next drone plans
around already-booked resources.

This is a practical prioritized-planning strategy:

- Deterministic and simple to reason about
- Fast enough for challenge maps
- Naturally enforces conflict avoidance

### 6. Output generation

Each drone path is expanded into a per-turn timeline (`on_hub`, `in_transit`,
`arrived`).
The simulation engine prints compact movement logs, then the renderer uses the
timeline for smooth playback.

## Visual Representation And UX Impact

The project includes an interactive Pygame viewer designed to make routing
decisions understandable at a glance.

Documented visual features:

- Automatic camera fit and scaling to current window size
- Hub rendering with zone-specific border styling
- Connection rendering with hover highlighting
- Drone interpolation between turns for smooth motion
- Overlap indicator (`xN`) when multiple drones share the same screen position
- Information overlays: FPS, turn counters, global statistics, keyboard
  shortcut panel, and hub/connection tooltips on hover
- Zone legend for quick semantic decoding

Keyboard controls:

- `P`: play/pause
- `R`: restart from turn 0
- Right arrow: step forward one turn
- Left arrow: step backward one turn
- `Q` or `Esc`: quit

How this improves user experience:

- Makes congestion points and route choices visible in real time.
- Helps debug capacities and zone effects without reading raw logs only.
- Enables quick comparison of map difficulty and planner behavior.

## Resources

### Topic references

- A* pathfinding overview: https://en.wikipedia.org/wiki/A*_search_algorithm
- Dijkstra shortest paths: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Pydantic documentation: https://docs.pydantic.dev/
- Pygame CE documentation: https://pyga.me/docs/

### AI usage 

- AI tool(s): Gemini
- Tasks assisted: README, structuring the code architecture, learning the algorithms.
- Validation approach: manual review of statements against source code

## Additional Notes

- Sample maps are available under `maps/` by difficulty level.
- The display requires a graphical environment compatible with Pygame.
