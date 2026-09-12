"""
End-to-end pipeline: transcript -> terms -> OntoLex RDF -> Wikidata interlinks.

Input is pre-transcribed Urdu text (from data/sample_utterances.jsonl, a
copy of the author's own Urdu Emergency Communication Corpus) rather than
live audio for this pilot run — the ASR stage (src/asr.py) is real, tested,
and pluggable ahead of this step, but this script demonstrates the
knowledge-graph construction stages, which is this project's actual
contribution.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.term_extraction import UrduTermExtractor
from src.ontolex_builder import OntoLexGraphBuilder
from src.wikidata_interlink import WikidataInterlinker

logger = logging.getLogger(__name__)


def run(input_path: str, output_path: str, limit: int | None, interlink: bool) -> dict:
    with open(input_path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    if limit:
        rows = rows[:limit]

    extractor = UrduTermExtractor()
    builder = OntoLexGraphBuilder()

    all_lemmas: set[tuple[str, str]] = set()
    for row in rows:
        terms = extractor.extract(row["text"])
        for term in terms:
            builder.add_term(term, source_id=row["id"])
            all_lemmas.add((term.lemma, term.upos))

    interlink_matches = 0
    if interlink:
        interlinker = WikidataInterlinker()
        for lemma, upos in all_lemmas:
            match = interlinker.find_match(lemma)
            if match:
                builder.add_interlink(lemma, upos, match)
                interlink_matches += 1

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    output_path_obj.write_text(builder.serialize(), encoding="utf-8")

    stats = {
        "utterances_processed": len(rows),
        "distinct_lexical_entries": len(all_lemmas),
        "triples_generated": len(builder.graph),
        "wikidata_interlinks_found": interlink_matches,
        "wikidata_interlink_attempted": len(all_lemmas) if interlink else 0,
    }
    return stats


def main():
    parser = argparse.ArgumentParser(description="Urdu transcript -> OntoLex-lemon RDF pipeline")
    parser.add_argument("--input", default="data/sample_utterances.jsonl")
    parser.add_argument("--output", default="output/urdu_emergency_lexicon.ttl")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-interlink", action="store_true", help="Skip live Wikidata lookups")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    stats = run(args.input, args.output, args.limit, interlink=not args.no_interlink)

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
