from pydantic import ValidationError
from src.exceptions import ParsingError
from src.models.map_models import MapConfig


class MapParser:
    @staticmethod
    def read_map_file(map_file_path: str) -> dict[str, list[str]]:
        try:
            with open(map_file_path, "r") as file:
                raw_config_data: dict[str, list[str]] = {}
                for i, line in enumerate(file):
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    splitted_line: list[str] = line.split(":")
                    if len(splitted_line) != 2:
                        raise ParsingError(
                            "line of the map must " "contain only one ':'\n",
                            i + 1,
                        )
                    key, info = splitted_line[0], splitted_line[1]
                    key = key.strip()
                    info = info.strip()
                    splitted_info: list[str] = info.split()
                    raw_config_data[key] = splitted_info
            return raw_config_data

        except OSError as e:
            raise ParsingError(str(e)) from OSError

    @classmethod
    def load_config(cls, map_file_path: str) -> MapConfig:
        raw_config_data = cls.read_map_file(map_file_path)
        try:

            return MapConfig.model_validate(raw_config_data)
        except ValidationError as e:
            raise ParsingError(f"{e}")
