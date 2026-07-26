"""
TMDB API Teszt Suite

Ez a fájl tartalmazza az összes API tesztet a TMDB (The Movie Database) API-hoz.

Teszt Struktúra:
- Funkcionális tesztek (TC01-TC06): Pozitív esetek, alap funkciók tesztelése
- Negatív tesztek (TC07-TC12): Hibás bemenetek, hibaüzenetek validálása
- Boundary Value Analysis (TC13-TC16): Határérték tesztelés (page paraméter-re)
- Nem-funkcionális tesztek (TC17-TC20): Teljesítmény és adat-integritás

Összesen: 20 teszt eset
Lefedettség: Funkcionális, negatív, határérték, teljesítmény, adat-validáció

Tesztadat-kezelés:
Ez a fájl fixture-ök segítségével (movies_data, search_queries_data,
auth_data, config_data - lásd conftest.py) a test_data/ mappában lévő
JSON fájlokból kapja a tesztadatokat, nem hardkódolva tartalmazza őket.
A TC13-TC16 határérték-tesztek pytest.mark.parametrize-ot használnak,
így egyetlen tesztfüggvény futtatja le mind a négy határérték-esetet a
pagination_boundaries.json alapján.
"""

import pytest
from api_requests import (
    get_popular_movies,
    get_movie_details,
    search_movie,
    get_movie_genres,
    get_with_custom_key
)
from conftest import load_test_data

# A parametrize dekorátornak collection time-kor kell az adat, ezért itt,
# modul szinten töltjük be (nem fixture-ön keresztül - lásd conftest.py
# load_test_data() docstringje a részletes magyarázatért)
pagination_boundaries = load_test_data("pagination_boundaries.json")

# --Funkcionális tesztek--
# Pozitív tesztek

def test_tc01_popular_movies():
    """TC01: Népszerű filmek lekérdezése"""
    response = get_popular_movies()
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_tc02_movie_details_valid_id(movies_data):
    """TC02: Film részletek érvényes ID-vel"""
    movie = movies_data["valid_movie"]
    response = get_movie_details(movie["id"])
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == movie["id"]
    assert data["title"] == movie["title"]
    assert "overview" in data

def test_tc03_search_movie_valid_query(search_queries_data):
    """TC03: Film keresés érvényes kifejezéssel"""
    query = search_queries_data["valid_query"]["value"]
    response = search_movie(query)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0

def test_tc04_get_genres():
    """TC04: Műfajok listájának lekérdezése"""
    response = get_movie_genres()
    assert response.status_code == 200
    data = response.json()
    assert "genres" in data
    for genre in data["genres"]:
        assert "id" in genre
        assert "name" in genre

def test_tc05_popular_movies_page_2():
    """TC05: Népszerű filmek 2. oldal"""
    response = get_popular_movies(page=2)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["results"]) > 0

def test_tc06_language_parameter(config_data):
    """TC06: Magyar nyelvi paraméter"""
    language = config_data["languages"]["hungarian"]
    response = get_popular_movies(language=language)
    assert response.status_code == 200

# --Negatív tesztek--
# Hitelesítési hibák

def test_tc07_invalid_api_key(auth_data):
    """TC07: Hibás API kulcs"""
    response = get_with_custom_key("movie/popular", api_key=auth_data["invalid_api_key"])
    assert response.status_code == 401

def test_tc08_missing_api_key():
    """TC08: Hiányzó API kulcs"""
    response = get_with_custom_key("movie/popular")
    assert response.status_code == 401

# Érvénytelen bemenet validáció
def test_tc09_invalid_movie_id(movies_data):
    """TC09: Érvénytelen film ID"""
    invalid_id = movies_data["invalid_movie_id"]["id"]
    response = get_movie_details(invalid_id)
    assert response.status_code in [400, 404]

def test_tc10_search_nonsense_query(search_queries_data):
    """TC10: Értelmetlen keresési kifejezés"""
    query = search_queries_data["nonsense_query"]["value"]
    response = search_movie(query)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0

def test_tc11_search_long_query(search_queries_data):
    """TC11: Hosszú keresési kifejezés"""
    long_query_spec = search_queries_data["long_query"]
    long_query = long_query_spec["character"] * long_query_spec["length"]
    response = search_movie(long_query)
    assert response.status_code == 200

def test_tc12_empty_search_query(search_queries_data):
    """TC12: Üres keresési string"""
    query = search_queries_data["empty_query"]["value"]
    response = search_movie(query)
    assert response.status_code in [200]
    data = response.json()
    assert len(data["results"]) == 0

# --2-pontos határérték-tesztek (BVA)--
# Dokumentáció alapján: Min:1, Max:500 oldalszám paraméter határok
# 100% határérték lefedettség
#
# A négy külön teszt (TC13-TC16) helyett egyetlen, parametrizált
# tesztfüggvény: ugyanazt a logikát futtatja le a
# pagination_boundaries.json-ban felsorolt mind a négy esetre.
# Az `ids` paraméter miatt a pytest kimenetben és a JSON riportban is
# külön-külön, TC13/TC14/TC15/TC16 néven jelennek meg az esetek.

@pytest.mark.parametrize(
    "boundary_case",
    pagination_boundaries,
    ids=[case["test_id"] for case in pagination_boundaries]
)
def test_boundary_pagination(boundary_case):
    """TC13-TC16: Oldalszám határérték tesztek (Boundary Value Analysis)"""
    response = get_popular_movies(page=boundary_case["page"])
    assert response.status_code == boundary_case["expected_status"], boundary_case["description"]

# --Nem-funkcionális tesztek--
# Teljesítmény tesztek

def test_tc17_response_time(config_data):
    """TC17: Válaszidő ellenőrzése konfigurált küszöbérték alapján"""
    import time
    threshold = config_data["performance_thresholds"]["max_response_time_seconds"]
    start = time.time()
    response = get_popular_movies()
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < threshold

def test_tc18_response_size(config_data):
    """TC18: JSON válasz méret ellenőrzés konfigurált küszöbérték alapján"""
    threshold = config_data["performance_thresholds"]["max_response_size_mb"]
    response = get_popular_movies()
    size_mb = len(response.content) / (1024 * 1024)
    assert size_mb < threshold

# Adat-integritás tesztek

def test_tc19_json_structure():
    """TC19: JSON struktúra ellenőrzése"""
    response = get_popular_movies()
    data = response.json()
    for movie in data["results"]:
        assert "id" in movie
        assert "title" in movie
        assert isinstance(movie["id"], int)

def test_tc20_data_types():
    """TC20: Adattípus ellenőrzés"""
    response = get_popular_movies()
    data = response.json()
    movie = data["results"][0]
    assert isinstance(movie["id"], int)
    assert isinstance(movie["title"], str)
    assert isinstance(movie.get("release_date"), (str, type(None)))