from src.models.map_config import MapConfig
from src.models.hub import Hub
from src.navigation.router import Router


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
