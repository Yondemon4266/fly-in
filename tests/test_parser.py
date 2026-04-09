import pytest
from pathlib import Path
from src.parser.parser import MapParser
from src.exceptions import ParsingError


TEST_DIR = Path(__file__).parent / "maps"
INVALID_MAPS_DIR = TEST_DIR / "invalids"
VALID_MAPS_DIR = TEST_DIR / "valids"


invalid_files = list(INVALID_MAPS_DIR.glob("*.txt"))
valid_files = list(VALID_MAPS_DIR.glob("*.txt"))


@pytest.mark.parametrize("file_path", invalid_files, ids=lambda p: p.name)
def test_parser_with_invalid_files(file_path):
    with pytest.raises(ParsingError) as exc_info:
        MapParser.parse(str(file_path))
    print(f"\n[TEST {file_path.name}] raised error : {exc_info.value}")


@pytest.mark.parametrize("file_path", valid_files, ids=lambda p: p.name)
def test_parser_with_valid_files(file_path):
    config = MapParser.parse(str(file_path))

    assert config is not None
    assert config.nb_drones > 0
