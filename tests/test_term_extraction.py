"""
Tests for UrduTermExtractor, run against the real Stanza Urdu UD pipeline
(downloaded on first use) rather than a mock — the whole point of this
module is that it uses genuine morphosyntactic analysis, not a lexicon
substring match, so a mock would test nothing meaningful.
"""

import pytest

from src.term_extraction import UrduTermExtractor


@pytest.fixture(scope="module")
def extractor():
    return UrduTermExtractor()


def test_extracts_content_words_with_correct_upos(extractor):
    terms = extractor.extract("جلدی آئیں مدد کریں")
    upos_by_surface = {t.surface: t.upos for t in terms}

    assert upos_by_surface["آئیں"] == "VERB"
    assert upos_by_surface["مدد"] == "NOUN"
    assert upos_by_surface["کریں"] == "VERB"


def test_lemmatizes_inflected_verb_forms(extractor):
    terms = extractor.extract("آئیں مدد کریں")
    lemmas = {t.surface: t.lemma for t in terms}

    # آئیں (imperative "come") lemmatizes to the infinitive آنا
    assert lemmas["آئیں"] == "آنا"


def test_deduplicates_repeated_lemma_within_one_call(extractor):
    terms = extractor.extract("ڈاکٹر ڈاکٹر ڈاکٹر")
    assert len(terms) == 1


def test_lexinfo_pos_mapping_matches_upos(extractor):
    terms = extractor.extract("ہلکا بخار ہے")
    for term in terms:
        if term.upos == "ADJ":
            assert term.lexinfo_pos == "adjective"
        if term.upos == "NOUN":
            assert term.lexinfo_pos == "noun"
