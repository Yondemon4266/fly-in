from enum import Enum


class DroneState(Enum):
    """Discrete drone states used by the animation timeline."""

    ON_HUB = "on_hub"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"


class DroneInfo:
    """Snapshot of a drone state at a specific simulation turn.

    Attributes:
        state: Current drone state.
        hub: Current hub name, or destination hub when in transit.
        from_hub: Source hub name when in transit.
    """

    def __init__(
        self, state: DroneState, hub: str, from_hub: str | None = None
    ):
        """Create a state snapshot for timeline storage.

        Args:
            state: Current drone state.
            hub: Hub linked to the current state.
            from_hub: Previous hub when state is in transit.
        """
        self.state = state
        self.hub = hub
        self.from_hub = from_hub


class Drone:
    """Drone model with raw route and derived per-turn timeline."""

    def __init__(self, drone_id: int) -> None:
        """Initialize an empty drone route.

        Args:
            drone_id: Unique numeric drone identifier.
        """
        self.id = drone_id
        self.raw_path: list[tuple[int, str]] = []
        self.timeline: dict[int, DroneInfo] = {}

    def generate_timeline(self, max_turn: int) -> None:
        """Expand raw route waypoints into turn-by-turn drone states.

        Args:
            max_turn: Last turn to materialize in the timeline.
        """
        self.timeline = {}
        if not self.raw_path:
            return

        for i in range(len(self.raw_path)):
            t, hub = self.raw_path[i]
            drone_info = DroneInfo(DroneState.ON_HUB, hub)

            self.timeline[t] = drone_info

            if i < len(self.raw_path) - 1:
                next_t, next_hub = self.raw_path[i + 1]
                for transit_t in range(t + 1, next_t):
                    transit_drone_info = DroneInfo(
                        DroneState.IN_TRANSIT, next_hub, hub
                    )
                    self.timeline[transit_t] = transit_drone_info
        final_t, final_hub = self.raw_path[-1]
        for t in range(final_t + 1, max_turn + 1):
            arrived_drone_info = DroneInfo(DroneState.ARRIVED, final_hub)
            self.timeline[t] = arrived_drone_info

    def get_state_at(self, turn: int) -> DroneInfo:
        """Return drone state for a given turn.

        Args:
            turn: Requested simulation turn.

        Returns:
            The state recorded for ``turn`` or the latest known state.
        """
        state = self.timeline.get(turn)
        if state is not None:
            return state
        last_known_turn = max(self.timeline.keys())
        return self.timeline[last_known_turn]
