"""
Builds a real, valid OntoLex-lemon RDF graph from extracted Urdu terms.

Uses the standard OntoLex-lemon (https://www.w3.org/2016/05/ontolex/) and
LexInfo (https://www.lexinfo.net/ontology/3.0/lexinfo) vocabularies. Each
distinct (lemma, part-of-speech) pair becomes one ontolex:LexicalEntry with
a canonical ontolex:Form and a minimal ontolex:LexicalSense — structurally
valid OntoLex, without inventing sense definitions the pipeline has no real
data for. Attestation (which source utterance a term came from) is recorded
via dct:source, which is genuine provenance rather than a fabricated gloss.

The base namespace below (example.org, per RFC 2606) is a placeholder for a
pilot that isn't hosted anywhere resolvable — swap it for a real namespace
before treating this as a published Linked Data resource.
"""

from __future__ import annotations

import re
from urllib.parse import quote

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS

from src.term_extraction import Term
from src.wikidata_interlink import InterlinkMatch

ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LEXINFO = Namespace("http://www.lexinfo.net/ontology/3.0/lexinfo#")
BASE = Namespace("http://example.org/urdu-emergency-lexicon/")

_LEXINFO_POS = {
    "noun": LEXINFO.noun,
    "properNoun": LEXINFO.properNoun,
    "verb": LEXINFO.verb,
    "adjective": LEXINFO.adjective,
    "adverb": LEXINFO.adverb,
}


def _slug(text: str) -> str:
    """URL-safe identifier fragment for a lemma. Urdu script survives
    percent-encoding fine; this just guards against whitespace/punctuation
    making an invalid URI fragment."""
    cleaned = re.sub(r"\s+", "_", text.strip())
    return quote(cleaned, safe="")


class OntoLexGraphBuilder:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("ontolex", ONTOLEX)
        self.graph.bind("lexinfo", LEXINFO)
        self.graph.bind("dct", DCTERMS)
        self.graph.bind("lex", BASE)
        self._entry_uris: dict[tuple[str, str], URIRef] = {}

    def add_term(self, term: Term, source_id: str) -> URIRef:
        """Add (or update, if already seen) a LexicalEntry for this term,
        recording `source_id` (the utterance it was attested in) as
        provenance. Returns the entry's URI."""
        key = (term.lemma, term.upos)
        if key in self._entry_uris:
            entry_uri = self._entry_uris[key]
        else:
            entry_uri = BASE[f"entry/{_slug(term.lemma)}_{term.upos.lower()}"]
            self._entry_uris[key] = entry_uri

            self.graph.add((entry_uri, RDF.type, ONTOLEX.LexicalEntry))
            self.graph.add((entry_uri, LEXINFO.partOfSpeech, _LEXINFO_POS[term.lexinfo_pos]))

            form_uri = BASE[f"form/{_slug(term.lemma)}_{term.upos.lower()}"]
            self.graph.add((form_uri, RDF.type, ONTOLEX.Form))
            self.graph.add((form_uri, ONTOLEX.writtenRep, Literal(term.lemma, lang="ur")))
            self.graph.add((entry_uri, ONTOLEX.canonicalForm, form_uri))

            sense_uri = BASE[f"sense/{_slug(term.lemma)}_{term.upos.lower()}"]
            self.graph.add((sense_uri, RDF.type, ONTOLEX.LexicalSense))
            self.graph.add((entry_uri, ONTOLEX.sense, sense_uri))

        # Attestation: which surface form, in which source utterance. Added
        # every time this term is seen, even for an already-created entry,
        # so an entry's provenance reflects every utterance it appeared in.
        self.graph.add((entry_uri, DCTERMS.source, Literal(source_id)))
        if term.surface != term.lemma:
            # ontolex:otherForm is an object property (LexicalEntry -> Form),
            # not a literal-valued shortcut like writtenRep -- each distinct
            # attested surface form gets its own ontolex:Form node, keyed on
            # the surface string so repeated attestations of the same
            # inflection reuse the same Form rather than duplicating it.
            other_form_uri = BASE[
                f"form/{_slug(term.lemma)}_{term.upos.lower()}/other/{_slug(term.surface)}"
            ]
            self.graph.add((other_form_uri, RDF.type, ONTOLEX.Form))
            self.graph.add((other_form_uri, ONTOLEX.writtenRep, Literal(term.surface, lang="ur")))
            self.graph.add((entry_uri, ONTOLEX.otherForm, other_form_uri))

        return entry_uri

    def add_interlink(self, lemma: str, upos: str, match: InterlinkMatch) -> None:
        """Record an external LLOD reference for this entry's sense, using
        ontolex:reference (sense -> concept it denotes), not owl:sameAs."""
        key = (lemma, upos)
        if key not in self._entry_uris:
            raise KeyError(f"No entry for {key}; call add_term first")
        sense_uri = BASE[f"sense/{_slug(lemma)}_{upos.lower()}"]
        self.graph.add((sense_uri, ONTOLEX.reference, URIRef(match.wikidata_uri)))

    def serialize(self, fmt: str = "turtle") -> str:
        return self.graph.serialize(format=fmt)
