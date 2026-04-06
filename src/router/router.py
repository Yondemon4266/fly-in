from src.models.map_config import MapConfig
from src.models.hub import Hub


class Router:
    def __init__(self, map_config: MapConfig):
        self.map_config = map_config
        self.hubs = self._init_hubs_dict(map_config.hubs)

    def _init_hubs_dict(self, list_hubs: list[Hub]) -> dict[str, Hub]:
        created_hubs: dict[str, Hub] = {}
        for hub in list_hubs:
            self.hubs[hub.name] = hub
        return created_hubs

    def calculate_distances_to_end_hub(self):
        