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

        # 1. Le VRAI max_turn est le dernier temps (index 0 du tuple) du trajet le plus long
        max_turn = max(path[-1][0] for path in all_drones_paths)

        print("\n" + "=" * 30)
        print("     SIMULATION RESULTS")
        print("=" * 30)

        # 2. On transforme les étapes en une ligne du temps complète pour chaque drone
        timelines: list[dict[int, str]] = []
        for path in all_drones_paths:
            timeline: dict[int, str] = {}
            for i in range(len(path)):
                t, hub = path[i]
                timeline[t] = hub

                # Si on a sauté un tour (zone restreinte), on comble le trou avec un statut "Transit"
                if i < len(path) - 1:
                    next_t, next_hub = path[i + 1]
                    for transit_t in range(t + 1, next_t):
                        timeline[transit_t] = f"Transit ({hub} -> {next_hub})"

            # On remplit tous les tours restants avec le statut "Arrived"
            final_t, final_hub = path[-1]
            for t in range(final_t + 1, max_turn + 1):
                timeline[t] = f"{final_hub} (Arrived)"

            timelines.append(timeline)

        # 3. L'affichage propre, en lisant la ligne du temps
        for current_turn in range(max_turn + 1):
            print(f"\n--- TURN {current_turn} ---")

            for drone_index, timeline in enumerate(timelines, start=1):
                status = timeline[current_turn]

                # Détection de l'attente (si on est au même endroit et qu'on ne bouge pas)
                if (
                    current_turn > 0
                    and status == timeline[current_turn - 1]
                    and "Arrived" not in status
                    and "Transit" not in status
                ):
                    print(f"Drone {drone_index} : {status} (Waiting)")
                else:
                    print(f"Drone {drone_index} : {status}")

        print("\n" + "=" * 30 + "\n")
