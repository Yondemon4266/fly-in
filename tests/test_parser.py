import pytest
from pathlib import Path
from src.parser.parser import MapParser
from src.exceptions import ParsingError

# 1. On définit les chemins vers nos dossiers de test
# Path(__file__).parent cible le dossier où se trouve le fichier test_parser.py
TEST_DIR = Path(__file__).parent / "maps"
INVALID_MAPS_DIR = TEST_DIR / "invalids"
VALID_MAPS_DIR = TEST_DIR / "valids"

# 2. On récupère la liste des chemins vers tous les fichiers .txt
# S'il n'y a pas encore de fichiers, ça renverra une liste vide
invalid_files = list(INVALID_MAPS_DIR.glob("*.txt"))
valid_files = list(VALID_MAPS_DIR.glob("*.txt"))


# 3. Tester les maps invalides
# L'argument 'ids' permet d'afficher le nom du fichier dans le terminal (plus lisible)
@pytest.mark.parametrize("file_path", invalid_files, ids=lambda p: p.name)
def test_parser_with_invalid_files(file_path):
    """Vérifie que les maps mal formées lèvent bien une ParsingError."""
    with pytest.raises(ParsingError):
        MapParser.parse(str(file_path))


# 4. Tester les maps valides
@pytest.mark.parametrize("file_path", valid_files, ids=lambda p: p.name)
def test_parser_with_valid_files(file_path):
    """Vérifie que les maps bien formées ne plantent pas."""
    # Si ça lève une exception, le test échouera, ce qui est le comportement voulu
    config = MapParser.parse(str(file_path))

    # On peut faire une vérification basique commune à toutes les maps valides
    assert config is not None
    assert config.nb_drones > 0
