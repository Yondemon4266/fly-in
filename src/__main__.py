import sys
from src.exceptions import ParsingError
from src.parser.parser import MapParser
from src.navigation.simulation_engine import SimulationEngine

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Provide one map file argument that ends with .txt")
        sys.exit(1)
    try:
        map_config = MapParser.parse(sys.argv[1])
        simulation_engine = SimulationEngine(map_config)
        simulation_engine.execute_turns()
    except OSError as e:
        sys.stderr.write(f"{e}")
        sys.exit(1)
    except ParsingError as e:
        sys.stderr.write(f"{e}")
        sys.exit(1)
