from src.models.map_config import MapConfig
from src.models.hub import Hub
import heapq
from src.models.hub_metadata import ZoneType
from src.exceptions import PathNotFoundError
from src.navigation.a_star_node import AStarNode
from src.models.connection import Connection
import sys


class Router:
    def __init__(self, map_config: MapConfig, hubs: dict[str, Hub]):
        self.map_config = map_config
        self.hubs = hubs
        self.distances_to_end = self._calculate_reverse_distances_dijkstra()

    def _calculate_reverse_distances_dijkstra(self) -> dict[str, int]:
        distances: dict[str, int] = {
            hub_name: sys.maxsize for hub_name in self.hubs
        }

        end_hub_name = self.map_config.end_hub.name
        distances[end_hub_name] = 0

        priority_queue = [(0, end_hub_name)]

        while priority_queue:
            current_dist, current_hub_name = heapq.heappop(priority_queue)

            if current_dist > distances[current_hub_name]:
                continue

            current_hub = self.hubs[current_hub_name]

            cost = 1

            zone_type = current_hub.metadata.zone

            if zone_type is ZoneType.BLOCKED:
                continue
            elif zone_type is ZoneType.RESTRICTED:
                cost = 2

            for connection in current_hub.connections:
                if connection.hub_a == current_hub_name:
                    neighbor_name = connection.hub_b
                else:
                    neighbor_name = connection.hub_a

                neighbor_hub = self.hubs[neighbor_name]
                neighbor_zone = neighbor_hub.metadata.zone
                if neighbor_zone is ZoneType.BLOCKED:
                    continue

                new_dist = current_dist + cost

                if new_dist < distances[neighbor_name]:
                    distances[neighbor_name] = new_dist
                    heapq.heappush(priority_queue, (new_dist, neighbor_name))

        start_hub_name = self.map_config.start_hub.name
        if distances[start_hub_name] == sys.maxsize:
            raise PathNotFoundError(
                f"Can't solve the map : no valid to path"
                f"between '{start_hub_name}' and '{end_hub_name}'."
            )

        return distances

    def a_star_path_finder(
        self, reservation_table: dict[tuple[int, str], int]
    ) -> list[tuple[int, str]]:
        start_hub_name = self.map_config.start_hub.name

        start_node = AStarNode(
            hub_name=start_hub_name,
            turns_from_start=0,
            total_estimated_turns=self._get_hub_distance(start_hub_name),
            parent=None,
        )
        priority_queue = [start_node]
        visited: set[tuple[int, str]] = set()
        while priority_queue:
            current_node = heapq.heappop(priority_queue)

            if current_node.hub_name == self.map_config.end_hub.name:
                return self._reconstruct_path(current_node)
            state_key = (current_node.turns_from_start, current_node.hub_name)
            if state_key in visited:
                continue
            visited.add(state_key)
            neighbors = self._get_neighbors(current_node, reservation_table)
            for neighbor in neighbors:
                heapq.heappush(priority_queue, neighbor)

        raise PathNotFoundError("No path found for this drone...")

    def _reconstruct_path(self, end_node: AStarNode) -> list[tuple[int, str]]:
        path: list[tuple[int, str]] = []
        current: AStarNode | None = end_node

        while current is not None:
            path.append((current.turns_from_start, current.hub_name))
            current = current.parent

        return path[::-1]

    def _get_hub_distance(self, hub_name: str) -> int:
        return self.distances_to_end.get(hub_name, sys.maxsize)

    def _is_unlimited_capacity(self, hub_name: str) -> bool:
        return hub_name in (
            self.map_config.start_hub.name,
            self.map_config.end_hub.name,
        )

    def _get_destination_name(
        self, connection: Connection, current_hub_name: str
    ) -> str:
        if connection.hub_a == current_hub_name:
            return connection.hub_b
        return connection.hub_a

    def _get_connection_name(self, connection: Connection) -> str:
        return f"{connection.hub_a}_{connection.hub_b}"

    def _create_wait_node(
        self,
        current_node: AStarNode,
        reservation_table: dict[tuple[int, str], int],
    ) -> AStarNode | None:
        arrival_turn = current_node.turns_from_start + 1
        current_hub = self.hubs[current_node.hub_name]

        drones_waiting = reservation_table.get(
            (arrival_turn, current_node.hub_name), 0
        )

        if (
            self._is_unlimited_capacity(current_node.hub_name)
            or drones_waiting < current_hub.metadata.max_drones
        ):
            total_estimated_turns = arrival_turn + self._get_hub_distance(
                current_node.hub_name
            )
            return AStarNode(
                hub_name=current_node.hub_name,
                turns_from_start=arrival_turn,
                total_estimated_turns=total_estimated_turns,
                parent=current_node,
            )
        return None

    def _create_normal_move_node(
        self,
        current_node: AStarNode,
        destination_hub: Hub,
        connection: Connection,
        reservation_table: dict[tuple[int, str], int],
    ) -> AStarNode | None:
        current_turn = current_node.turns_from_start
        arrival_turn = current_turn + 1
        connection_name = self._get_connection_name(connection)

        drones_in_connection = reservation_table.get(
            (current_turn, connection_name), 0
        )
        if drones_in_connection >= connection.metadata.max_link_capacity:
            return None

        drones_at_destination = reservation_table.get(
            (arrival_turn, destination_hub.name), 0
        )
        if not self._is_unlimited_capacity(destination_hub.name):
            if drones_at_destination >= destination_hub.metadata.max_drones:
                return None

        total_estimated_turns = arrival_turn + self._get_hub_distance(
            destination_hub.name
        )
        return AStarNode(
            hub_name=destination_hub.name,
            turns_from_start=arrival_turn,
            total_estimated_turns=total_estimated_turns,
            parent=current_node,
        )

    def _create_restricted_move_node(
        self,
        current_node: AStarNode,
        destination_hub: Hub,
        connection: Connection,
        reservation_table: dict[tuple[int, str], int],
    ) -> AStarNode | None:
        current_turn = current_node.turns_from_start
        arrival_turn = current_turn + 2
        connection_name = self._get_connection_name(connection)

        drones_at_departure = reservation_table.get(
            (current_turn, connection_name), 0
        )
        if drones_at_departure >= connection.metadata.max_link_capacity:
            return None

        drones_in_transit = reservation_table.get(
            (current_turn + 1, connection_name), 0
        )
        if drones_in_transit >= connection.metadata.max_link_capacity:
            return None

        drones_at_destination = reservation_table.get(
            (arrival_turn, destination_hub.name), 0
        )
        if not self._is_unlimited_capacity(destination_hub.name):
            if drones_at_destination >= destination_hub.metadata.max_drones:
                return None

        total_estimated_turns = arrival_turn + self._get_hub_distance(
            destination_hub.name
        )
        return AStarNode(
            hub_name=destination_hub.name,
            turns_from_start=arrival_turn,
            total_estimated_turns=total_estimated_turns,
            parent=current_node,
        )

    def _get_neighbors(
        self,
        current_node: AStarNode,
        reservation_table: dict[tuple[int, str], int],
    ) -> list[AStarNode]:
        neighbors: list[AStarNode] = []

        wait_node = self._create_wait_node(current_node, reservation_table)
        if wait_node is not None:
            neighbors.append(wait_node)

        current_hub = self.hubs[current_node.hub_name]

        for connection in current_hub.connections:
            destination_name = self._get_destination_name(
                connection, current_node.hub_name
            )
            destination_hub = self.hubs[destination_name]

            if destination_hub.metadata.zone is ZoneType.BLOCKED:
                continue

            if destination_hub.metadata.zone in (
                ZoneType.NORMAL,
                ZoneType.PRIORITY,
            ):
                move_node = self._create_normal_move_node(
                    current_node,
                    destination_hub,
                    connection,
                    reservation_table,
                )
                if move_node is not None:
                    neighbors.append(move_node)

            elif destination_hub.metadata.zone is ZoneType.RESTRICTED:
                restricted_move_node = self._create_restricted_move_node(
                    current_node,
                    destination_hub,
                    connection,
                    reservation_table,
                )
                if restricted_move_node is not None:
                    neighbors.append(restricted_move_node)

        return neighbors
