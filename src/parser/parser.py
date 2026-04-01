from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ValidationError,
    ConfigDict,
)
from typing import Any
from src.parser.parser_utils import ParserUtils
import sys
from pathlib import Path


class MapParser:

    @staticmethod
    def parse_map_file(file_path: str):
        path = Path(file_path)
        if path.suffix != ".txt":
            raise Exception("File must end with '.txt'")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Provide one map file argument that ends with .txt")
        sys.exit(1)
    try:
        MapParser.parse_map_file(sys.argv[1])
    except Exception as e:
        sys.stderr.write(f"{e}")
