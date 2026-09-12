"""
Morpho-syntactic term extraction for Urdu transcripts.

Uses Stanza's Urdu Universal Dependencies model for real tokenization,
POS-tagging, and lemmatization (not a lexicon-substring heuristic) to
identify candidate lexical entries — content words (nouns, verbs,
adjectives, adverbs) — worth promoting to OntoLex-lemon LexicalEntry nodes.
"""

from __future__ import annotations

from dataclasses import dataclass

import stanza

CONTENT_UPOS = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}

_UPOS_TO_LEXINFO = {
    "NOUN": "noun",
    "PROPN": "properNoun",
    "VERB": "verb",
    "ADJ": "adjective",
    "ADV": "adverb",
}


@dataclass(frozen=True)
class Term:
    surface: str
    lemma: str
    upos: str
    lexinfo_pos: str


class UrduTermExtractor:
    """Thin, testable wrapper around a Stanza Urdu pipeline. Downloads the
    'ur' model on first use (stanza.download), which requires network access
    once; the pipeline itself runs fully offline afterwards."""

    def __init__(self):
        stanza.download("ur", verbose=False)
        self._nlp = stanza.Pipeline("ur", processors="tokenize,pos,lemma", verbose=False)

    def extract(self, text: str) -> list[Term]:
        doc = self._nlp(text)
        terms: list[Term] = []
        seen = set()
        for sentence in doc.sentences:
            for word in sentence.words:
                if word.upos not in CONTENT_UPOS:
                    continue
                key = (word.lemma, word.upos)
                if key in seen:
                    continue
                seen.add(key)
                terms.append(
                    Term(
                        surface=word.text,
                        lemma=word.lemma or word.text,
                        upos=word.upos,
                        lexinfo_pos=_UPOS_TO_LEXINFO[word.upos],
                    )
                )
        return terms
