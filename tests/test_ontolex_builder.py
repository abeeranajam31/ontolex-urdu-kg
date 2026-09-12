"""
Tests for OntoLexGraphBuilder: valid RDF structure, round-trip
serialization, multi-attestation provenance, and interlinking — all
checked against the actual rdflib Graph, not mocked.
"""

import pytest
from rdflib import Graph, RDF

from src.ontolex_builder import ONTOLEX, LEXINFO, OntoLexGraphBuilder
from src.term_extraction import Term
from src.wikidata_interlink import InterlinkMatch


@pytest.fixture
def sample_term():
    return Term(surface="ڈاکٹر", lemma="ڈاکٹر", upos="NOUN", lexinfo_pos="noun")


def test_add_term_creates_lexical_entry_form_and_sense(sample_term):
    builder = OntoLexGraphBuilder()
    entry_uri = builder.add_term(sample_term, source_id="UEC-001")

    assert (entry_uri, RDF.type, ONTOLEX.LexicalEntry) in builder.graph
    assert (entry_uri, LEXINFO.partOfSpeech, LEXINFO.noun) in builder.graph

    forms = list(builder.graph.objects(entry_uri, ONTOLEX.canonicalForm))
    assert len(forms) == 1
    assert (forms[0], RDF.type, ONTOLEX.Form) in builder.graph

    senses = list(builder.graph.objects(entry_uri, ONTOLEX.sense))
    assert len(senses) == 1
    assert (senses[0], RDF.type, ONTOLEX.LexicalSense) in builder.graph


def test_same_lemma_seen_twice_creates_one_entry_with_two_sources(sample_term):
    builder = OntoLexGraphBuilder()
    uri1 = builder.add_term(sample_term, source_id="UEC-001")
    uri2 = builder.add_term(sample_term, source_id="UEC-002")

    assert uri1 == uri2
    entry_count = sum(1 for _ in builder.graph.subjects(RDF.type, ONTOLEX.LexicalEntry))
    assert entry_count == 1

    from rdflib.namespace import DCTERMS
    sources = set(builder.graph.objects(uri1, DCTERMS.source))
    assert len(sources) == 2


def test_serialized_turtle_round_trips(sample_term):
    builder = OntoLexGraphBuilder()
    builder.add_term(sample_term, source_id="UEC-001")

    ttl = builder.serialize()
    reparsed = Graph()
    reparsed.parse(data=ttl, format="turtle")

    assert len(reparsed) == len(builder.graph)


def test_add_interlink_attaches_ontolex_reference_to_sense(sample_term):
    builder = OntoLexGraphBuilder()
    builder.add_term(sample_term, source_id="UEC-001")
    match = InterlinkMatch(lemma="ڈاکٹر", wikidata_uri="http://www.wikidata.org/entity/Q4618975", english_label="Doctor")

    builder.add_interlink("ڈاکٹر", "NOUN", match)

    from rdflib import URIRef
    triples = list(builder.graph.triples((None, ONTOLEX.reference, URIRef(match.wikidata_uri))))
    assert len(triples) == 1


def test_add_interlink_without_prior_term_raises():
    builder = OntoLexGraphBuilder()
    match = InterlinkMatch(lemma="x", wikidata_uri="http://example.org/x", english_label=None)
    with pytest.raises(KeyError):
        builder.add_interlink("x", "NOUN", match)
