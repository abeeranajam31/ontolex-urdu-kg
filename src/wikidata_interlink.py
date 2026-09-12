"""
Interlinks LexicalSense nodes to external Linguistic Linked Open Data (LLOD)
concepts by querying Wikidata's live public SPARQL endpoint for an exact
Urdu-language label match. Uses `ontolex:reference` (a LexicalSense pointing
at the external concept it denotes) — the OntoLex-lemon-recommended pattern
for this, rather than owl:sameAs, since a lexical sense and a Wikidata item
are not the same kind of thing (one is a sense, one is a real-world/concept
entity the sense refers to).

Genuinely queries a remote, third-party service at runtime — network
failures or the absence of a match are expected, non-error outcomes, not
something to paper over with a fabricated link.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "ontolex-urdu-kg/0.1 (research pilot; github.com/abeeranajam31)"


@dataclass(frozen=True)
class InterlinkMatch:
    lemma: str
    wikidata_uri: str
    english_label: str | None


class WikidataInterlinker:
    def __init__(self, endpoint: str = WIKIDATA_ENDPOINT, timeout_s: int = 10):
        self._sparql = SPARQLWrapper(endpoint, agent=USER_AGENT)
        self._sparql.setReturnFormat(JSON)
        self._sparql.setTimeout(timeout_s)

    def find_match(self, lemma: str) -> InterlinkMatch | None:
        """Exact Urdu-label lookup. Returns the first match, or None if the
        query fails (network/timeout) or nothing matches — both real,
        expected outcomes for a live lookup against a term that may simply
        not exist in Wikidata."""
        escaped = lemma.replace('"', '\\"')
        query = f"""
        SELECT ?item ?englishLabel WHERE {{
          ?item rdfs:label "{escaped}"@ur .
          OPTIONAL {{ ?item rdfs:label ?englishLabel . FILTER(LANG(?englishLabel) = "en") }}
        }}
        LIMIT 1
        """
        self._sparql.setQuery(query)
        try:
            results = self._sparql.query().convert()
        except Exception as e:
            logger.warning(f"Wikidata lookup failed for '{lemma}': {e}")
            return None

        bindings = results.get("results", {}).get("bindings", [])
        if not bindings:
            return None

        row = bindings[0]
        return InterlinkMatch(
            lemma=lemma,
            wikidata_uri=row["item"]["value"],
            english_label=row.get("englishLabel", {}).get("value"),
        )
