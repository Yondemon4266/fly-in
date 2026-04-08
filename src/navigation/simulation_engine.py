from src.models.map_config import MapConfig
from src.models.hub import Hub
from src.navigation.router import Router
from src.exceptions import ConnectionNotFoundError
from src.display.drone import Drone


class SimulationEngine:

    def __init__(self, map_config: MapConfig) -> None:
        self.map_config = map_config
        self.hubs = self._init_hubs_dict(map_config.hubs)
        self.pathfinder = Router(self.map_config, self.hubs)
        self.reservation_table: dict[tuple[int, str], int] = {}

    def _init_hubs_dict(self, list_hubs: list[Hub]) -> dict[str, Hub]:
        created_hubs: dict[str, Hub] = {}
        for hub in list_hubs:
            created_hubs[hub.name] = hub
        return created_hubs

    def _update_reservations(self, path: list[tuple[int, str]]) -> None:
        t_start, start_hub = path[0]
        self.reservation_table[(t_start, start_hub)] = (
            self.reservation_table.get((t_start, start_hub), 0) + 1
        )

        for i in range(len(path) - 1):
            t_current, current_hub = path[i]
            t_next, next_hub = path[i + 1]

            self.reservation_table[(t_next, next_hub)] = (
                self.reservation_table.get((t_next, next_hub), 0) + 1
            )

            if current_hub != next_hub:
                connection_name = self._get_connection_name_from_hubs(
                    current_hub, next_hub
                )

                for t in range(t_current, t_next):
                    self.reservation_table[(t, connection_name)] = (
                        self.reservation_table.get((t, connection_name), 0) + 1
                    )

    def _get_connection_name_from_hubs(
        self, hub1_name: str, hub2_name: str
    ) -> str:
        for connection in self.hubs[hub1_name].connections:
            if connection.hub_a == hub2_name or connection.hub_b == hub2_name:
                return f"{connection.hub_a}_{connection.hub_b}"
        raise ConnectionNotFoundError(
            f"Can't find connection between {hub1_name} {hub2_name}!"
        )

    def plan_drone_schedules(self) -> None:
        self.drones: list[Drone] = []

        for i in range(self.map_config.nb_drones):
            drone = Drone(drone_id=i + 1)
            drone_temporal_path = self.pathfinder.a_star_path_finder(
                self.reservation_table
            )

            self._update_reservations(drone_temporal_path)
            drone.raw_path = drone_temporal_path
            self.drones.append(drone)

        max_turn = 0
        if self.drones:
            max_turn = max(
                drone.raw_path[-1][0]
                for drone in self.drones
                if drone.raw_path
            )

        for drone in self.drones:
            drone.generate_timeline(max_turn)
