"""
Tests for WikidataInterlinker. Mocks SPARQLWrapper.query() so these run
deterministically in CI regardless of the live public Wikidata endpoint's
availability (it rate-limits aggressively and has real outages — observed
directly during development, see README) — a live-network integration test
would be flaky by construction.
"""

from unittest.mock import MagicMock, patch

from src.wikidata_interlink import WikidataInterlinker


def _mock_response(bindings):
    mock_result = MagicMock()
    mock_result.convert.return_value = {"results": {"bindings": bindings}}
    return mock_result


def test_successful_match_returns_uri_and_label():
    interlinker = WikidataInterlinker()
    bindings = [{
        "item": {"value": "http://www.wikidata.org/entity/Q4618975"},
        "englishLabel": {"value": "Doctor"},
    }]
    with patch.object(interlinker._sparql, "query", return_value=_mock_response(bindings)):
        match = interlinker.find_match("ڈاکٹر")

    assert match is not None
    assert match.wikidata_uri == "http://www.wikidata.org/entity/Q4618975"
    assert match.english_label == "Doctor"
    assert match.lemma == "ڈاکٹر"


def test_no_match_returns_none():
    interlinker = WikidataInterlinker()
    with patch.object(interlinker._sparql, "query", return_value=_mock_response([])):
        match = interlinker.find_match("some-nonexistent-term-xyz")

    assert match is None


def test_network_failure_returns_none_not_exception():
    """The exact failure mode observed live during development: Wikidata's
    endpoint returning HTTP 429 under rate-limiting. Must degrade to None,
    not propagate and crash the pipeline."""
    interlinker = WikidataInterlinker()
    with patch.object(interlinker._sparql, "query", side_effect=Exception("HTTP Error 429: rate-limited")):
        match = interlinker.find_match("ڈاکٹر")

    assert match is None


def test_quote_in_lemma_does_not_break_query():
    """A lemma containing a double-quote must not break out of the SPARQL
    string literal it's interpolated into."""
    interlinker = WikidataInterlinker()
    captured_query = {}

    def fake_set_query(q):
        captured_query["value"] = q

    with patch.object(interlinker._sparql, "setQuery", side_effect=fake_set_query), \
         patch.object(interlinker._sparql, "query", return_value=_mock_response([])):
        interlinker.find_match('a"b')

    assert '\\"' in captured_query["value"]
