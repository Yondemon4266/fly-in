import sys
from src.parser import MapParser
from src.exceptions import FlyInError


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("No map provided, please provide one map file path\n")
        sys.exit(1)
    file_path: str = sys.argv[1]

    try:
        MapParser.load_config(file_path)
    except FlyInError as e:
        sys.stderr.write(f"\n{e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
