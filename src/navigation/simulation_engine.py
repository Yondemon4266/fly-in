from src.models.map_config import MapConfig
from src.models.hub import Hub
from src.navigation.router import Router
from src.exceptions import ConnectionNotFoundError


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

    def execute_turns(self) -> None:
        self.all_drones_paths: list[list[tuple[int, str]]] = []
        for _ in range(self.map_config.nb_drones):
            drone_temporal_path = self.pathfinder.a_star_path_finder(
                self.reservation_table
            )
            self._update_reservations(drone_temporal_path)
            self.all_drones_paths.append(drone_temporal_path)
        self._display_simulation(self.all_drones_paths)

    def _display_simulation(
        self, all_drones_paths: list[list[tuple[int, str]]]
    ) -> None:
        if not all_drones_paths:
            print("No paths to display.")
            return

        max_turn = max(len(path) - 1 for path in all_drones_paths)

        print("\n" + "=" * 30)
        print("     SIMULATION RESULTS")
        print("=" * 30)

        for current_turn in range(max_turn + 1):
            print(f"\n--- TURN {current_turn} ---")

            for drone_index, path in enumerate(all_drones_paths, start=1):
                if current_turn < len(path):
                    current_hub = path[current_turn][1]

                    status = ""
                    if (
                        current_turn > 0
                        and path[current_turn][1] == path[current_turn - 1][1]
                    ):
                        status = " (Waiting)"

                    print(f"Drone {drone_index} : {current_hub}{status}")
                else:
                    final_hub = path[-1][1]
                    print(f"Drone {drone_index} : {final_hub} (Arrived)")

        print("\n" + "=" * 30 + "\n")
