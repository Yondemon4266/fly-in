from pydantic import (
    ValidationError,
)
from typing import Optional
from src.parser.parser_utils import ParserUtils
import sys
from pathlib import Path
from src.exceptions import ParsingError
from src.models.hub import Hub
from src.models.connection import Connection
from src.models.map_config import MapConfig


class MapParser:
    def __init__(self) -> None:
        self.nb_drones: Optional[int] = None
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self.hubs: dict[str, Hub] = {}
        self.connections: dict[str, Connection] = {}
        self.seen_coordinates: set[tuple[int, int]] = set()

    @classmethod
    def parse(cls, file_path: str) -> MapConfig:
        path = Path(file_path)
        if path.suffix != ".txt":
            raise OSError("File must end with '.txt'")

        parser = cls()
        parser._read_file(path)
        if parser.nb_drones is None:
            raise ParsingError("Missing mandatory key 'nb_drones' in file.")
        if parser.start_hub is None:
            raise ParsingError("Missing mandatory key 'start_hub' in file.")
        if parser.end_hub is None:
            raise ParsingError("Missing mandatory key 'end_hub' in file.")
        if not parser.start_hub.connections:
            raise ParsingError(
                f"start_hub '{parser.start_hub.name}' is isolated."
            )
        if not parser.end_hub.connections:
            raise ParsingError(f"end_hub '{parser.end_hub.name}' is isolated.")
        try:
            return MapConfig(
                nb_drones=parser.nb_drones,
                start_hub=parser.start_hub,
                end_hub=parser.end_hub,
                hubs=list(parser.hubs.values()),
                connections=list(parser.connections.values()),
            )
        except ValidationError as e:
            ParserUtils.print_formatted_errors(e)
            raise ParsingError("Invalid data format for hub or connection")

    def _read_file(self, path: Path) -> None:
        with open(path, "r") as file:
            for i, line in enumerate(file):
                line_number = i + 1
                self._parse_line(line, line_number)

    def _parse_line(self, line: str, line_number: int) -> None:
        line = line.strip()
        if not line or line.startswith("#"):
            return

        splitted_line = line.split(":")
        if len(splitted_line) != 2:
            raise ParsingError(
                f"Can't be more than one ':' in '{line}'", line_number
            )
        key = splitted_line[0].strip()
        info = splitted_line[1].strip()
        if self.nb_drones is None and key != "nb_drones":
            raise ParsingError("First key must be 'nb_drones'", line_number)

        self._route_key(key, info, line_number)

    def _route_key(self, key: str, info: str, line_number: int) -> None:
        try:
            match key:
                case "nb_drones":
                    self._handle_nb_drones(info, line_number)
                case "start_hub":
                    self._handle_start_hub(info, line_number)
                case "end_hub":
                    self._handle_end_hub(info, line_number)
                case "hub":
                    self._handle_hub(info, line_number)
                case "connection":
                    self._handle_connection(info, line_number)
                case _:
                    raise ParsingError(f"Unknown key '{key}'", line_number)
        except ValidationError as e:
            ParserUtils.print_formatted_errors(e)
            raise ParsingError(
                "Invalid data format for hub or connection", line_number
            )

    def _handle_nb_drones(self, info: str, line_number: int) -> None:
        try:
            self.nb_drones = int(info)
            if self.nb_drones < 1:
                raise ParsingError(
                    "nb_drones key must be positive int value. "
                    f"input '{info}'",
                    line_number,
                )
        except ValueError as e:
            raise ParsingError(
                f"nb_drones key must have a positive int value. input '{e}'",
                line_number,
            )

    def _handle_start_hub(self, info: str, line_number: int) -> None:
        if self.start_hub:
            raise ParsingError("start_hub already defined", line_number)
        self.start_hub = Hub.model_validate(info)
        self._check_and_add_coordinates(self.start_hub, line_number)
        if self.start_hub.name in self.hubs:
            raise ParsingError(
                "Hub {self.start_hub.name} already declared in hubs",
                line_number,
            )
        if not self.nb_drones:
            raise ParsingError(
                "nb_drones key must be declared first.'",
                line_number,
            )
        self.start_hub.metadata.max_drones = self.nb_drones
        self.hubs[self.start_hub.name] = self.start_hub

    def _handle_end_hub(self, info: str, line_number: int) -> None:
        if self.end_hub:
            raise ParsingError("end_hub already defined", line_number)

        self.end_hub = Hub.model_validate(info)
        self._check_and_add_coordinates(self.end_hub, line_number)

        if self.end_hub.name in self.hubs:
            raise ParsingError(
                f"Hub {self.end_hub.name} already declared in hubs",
                line_number,
            )
        if not self.nb_drones:
            raise ParsingError(
                "nb_drones key must be declared first.'",
                line_number,
            )
        self.end_hub.metadata.max_drones = self.nb_drones
        self.hubs[self.end_hub.name] = self.end_hub

    def _handle_hub(self, info: str, line_number: int) -> None:
        new_hub = Hub.model_validate(info)
        self._check_and_add_coordinates(new_hub, line_number)

        if new_hub.name in self.hubs:
            raise ParsingError(
                f"Hub {new_hub.name} already declared in hubs",
                line_number,
            )
        self.hubs[new_hub.name] = new_hub

    def _handle_connection(self, info: str, line_number: int) -> None:
        connection = Connection.model_validate(info)

        hub_a_name = connection.hub_a
        hub_b_name = connection.hub_b
        conn_key_1 = f"{hub_a_name}_{hub_b_name}"
        conn_key_2 = f"{hub_b_name}_{hub_a_name}"

        if hub_a_name not in self.hubs:
            raise ParsingError(
                f"hub '{hub_a_name}' must be declared before connection",
                line_number,
            )
        if hub_b_name not in self.hubs:
            raise ParsingError(
                f"hub '{hub_b_name}' must be declared before connection",
                line_number,
            )

        if conn_key_1 in self.connections or conn_key_2 in self.connections:
            raise ParsingError(
                f"Connection {info} declared twice.", line_number
            )

        self.connections[conn_key_1] = connection
        self.hubs[hub_a_name].connections.append(connection)
        self.hubs[hub_b_name].connections.append(connection)

    def _check_and_add_coordinates(self, hub: Hub, line_number: int) -> None:
        coords = (hub.x, hub.y)
        if coords in self.seen_coordinates:
            raise ParsingError(
                f"Coordinates {coords} for hub '{hub.name}'"
                " are already taken.",
                line_number,
            )
        self.seen_coordinates.add(coords)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Provide one map file argument that ends with .txt")
        sys.exit(1)
    try:
        map_config = MapParser.parse(sys.argv[1])
        print(map_config.connections)
    except OSError as e:
        sys.stderr.write(f"{e}")
        sys.exit(1)
    except ParsingError as e:
        sys.stderr.write(f"{e}")
        sys.exit(1)
