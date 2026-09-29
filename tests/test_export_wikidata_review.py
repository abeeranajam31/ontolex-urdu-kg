"""
Tests for the Wikidata review export, run against the lexicon this repo
actually publishes (output/urdu_emergency_lexicon.ttl).
"""

from pathlib import Path

from scripts.export_wikidata_review import LEXICAL_CATEGORY_QID, build_rows

REPO = Path(__file__).resolve().parents[1]
LEXICON = REPO / "output" / "urdu_emergency_lexicon.ttl"
CORPUS = REPO / "data" / "sample_utterances.jsonl"


def test_one_row_per_lexical_entry():
    rows = build_rows(LEXICON, CORPUS)
    assert len(rows) == 207
    assert len({(r["lemma"], r["pos"]) for r in rows}) == len(rows)


def test_every_pos_maps_to_a_lexical_category():
    rows = build_rows(LEXICON, CORPUS)
    assert all(r["pos"] in LEXICAL_CATEGORY_QID for r in rows)
    assert all(r["lexical_category_qid"] for r in rows)


def test_examples_come_from_attesting_utterances():
    rows = build_rows(LEXICON, CORPUS)
    for r in rows:
        assert r["attestations"] >= 1
        assert r["example_text"]


def test_review_columns_start_empty():
    rows = build_rows(LEXICON, CORPUS)
    assert all(r["keep"] == r["on_wikidata"] == r["lexeme_id"] == "" for r in rows)
