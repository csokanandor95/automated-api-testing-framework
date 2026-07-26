"""
conftest.py - Megosztott pytest fixture-ök és tesztadat-kezelés

A conftest.py egy pytest által automatikusan felismert speciális fájl:
mindent, amit itt definiálunk, minden tesztfájl (jelen esetben a
test_cases.py) automatikusan lát, anélkül hogy importálni kellene.

Ez a fájl felelős azért, hogy a test_cases.py-ba a
tesztadatokat betöltse a test_data/ mappában lévő JSON fájlokból, és
fixture-ök formájában elérhetővé tegye a tesztek számára.

Előnyök:
- A tesztadat és a tesztlogika szét van választva (Separation of Concerns)
- Új tesztadat hozzáadásához NEM kell Python kódot módosítani, elég egy
  JSON fájlt szerkeszteni
- A tesztadatok domén szerint, jól látható struktúrában vannak
- A scope="session" beállítás miatt egy tesztfutás alatt csak egyszer
  töltődnek be a fájlok, nem minden egyes teszt előtt újra
"""
import json
from pathlib import Path

import pytest

# A test_data/ mappa a projekt gyökerében található, a src/ mappa mellett.
# Ugyanazt a mintát követi, mint a report_generator.py get_project_root()
# függvénye: a conftest.py a src/ mappában van, ezért egyet lépünk vissza.
TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def load_test_data(filename: str):
    """
    Segédfüggvény egy JSON tesztadat-fájl betöltésére.

    Szándékosan NEM fixture, hanem sima Python függvény: a
    @pytest.mark.parametrize dekorátornak "collection time"-kor
    (vagyis amikor pytest beolvassa és felépíti a tesztlistát, még a
    tényleges futtatás ELŐTT) kell megkapnia az adatot. A fixture-ök
    viszont csak "test execution time"-kor, egy adott teszt tényleges
    futtatásakor állnak elő. Emiatt ahol parametrize-hoz kell adat
    (lásd test_cases.py - test_boundary_pagination), ott ezt a
    függvényt importáljuk közvetlenül, nem fixture-ön keresztül kérjük.
    """
    filepath = TEST_DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def movies_data():
    """Film-tesztadatok: érvényes és érvénytelen film ID-k (movies.json)"""
    return load_test_data("movies.json")


@pytest.fixture(scope="session")
def search_queries_data():
    """Keresési kifejezés tesztadatok (search_queries.json)"""
    return load_test_data("search_queries.json")


@pytest.fixture(scope="session")
def auth_data():
    """Hitelesítési tesztadatok, pl. érvénytelen API kulcs (auth.json)"""
    return load_test_data("auth.json")


@pytest.fixture(scope="session")
def config_data():
    """Általános konfiguráció: nyelvi kódok, teljesítmény küszöbértékek (config.json)"""
    return load_test_data("config.json")