"""Tests the SPARQL HTTP endpoint against a small in-test graph (not the
full generated corpus), via FastAPI's TestClient — a real HTTP request/
response cycle through the actual query-execution code path."""

import pytest
from fastapi.testclient import TestClient

from src.ontolex_builder import OntoLexGraphBuilder
from src.term_extraction import Term


@pytest.fixture
def client(tmp_path, monkeypatch):
    builder = OntoLexGraphBuilder()
    builder.add_term(Term(surface="ڈاکٹر", lemma="ڈاکٹر", upos="NOUN", lexinfo_pos="noun"), source_id="TEST-001")
    graph_path = tmp_path / "test_graph.ttl"
    graph_path.write_text(builder.serialize(), encoding="utf-8")

    monkeypatch.setenv("ONTOLEX_GRAPH_PATH", str(graph_path))

    from src import sparql_service
    sparql_service._graph = sparql_service.Graph()  # reset shared module-level graph between tests
    sparql_service.GRAPH_PATH = str(graph_path)
    sparql_service.load_graph()

    return TestClient(sparql_service.app)


def test_health_reports_loaded_triple_count(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["triples_loaded"] > 0


def test_sparql_query_returns_expected_entry(client):
    query = """
    PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
    SELECT ?form WHERE {
      ?entry a ontolex:LexicalEntry ; ontolex:canonicalForm ?f .
      ?f ontolex:writtenRep ?form .
    }
    """
    r = client.get("/sparql", params={"query": query})
    assert r.status_code == 200
    bindings = r.json()["results"]["bindings"]
    assert any(b["form"]["value"] == "ڈاکٹر" for b in bindings)


def test_invalid_sparql_returns_400(client):
    r = client.get("/sparql", params={"query": "NOT VALID SPARQL"})
    assert r.status_code == 400
