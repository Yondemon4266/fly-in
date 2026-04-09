from enum import Enum


class DroneState(Enum):
    ON_HUB = "on_hub"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"


class DroneInfo:
    def __init__(
        self, state: DroneState, hub: str, from_hub: str | None = None
    ):
        self.state = state
        self.hub = hub
        self.from_hub = from_hub


class Drone:
    def __init__(self, drone_id: int) -> None:
        self.id = drone_id
        self.raw_path: list[tuple[int, str]] = []
        self.timeline: dict[int, DroneInfo] = {}

    def generate_timeline(self, max_turn: int) -> None:
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
        state = self.timeline.get(turn)
        if state is not None:
            return state
        last_known_turn = max(self.timeline.keys())
        return self.timeline[last_known_turn]
