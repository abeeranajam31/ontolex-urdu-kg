"""
Export the OntoLex lexicon as a review sheet for contributing Urdu
lexemes to Wikidata.

Stanza's lemmatizer is automatic, so not every entry is a real Urdu
lemma (fragments such as single letters do occur). Nothing should go
to Wikidata unreviewed. This script produces one CSV row per lexical
entry with everything a reviewer needs to decide, and to fill in the
Wikidata new-lexeme form by hand:

  lemma, lexinfo POS, the Wikidata lexical-category item for that POS,
  other attested forms, how many utterances attest it, and one example
  sentence with its English gloss.

The last three columns (keep, on_wikidata, lexeme_id) are left empty
for the reviewer: mark keep=y for real lemmas, check whether Wikidata
already has the lexeme, and record the L-id once it exists.

Usage:
    python -m scripts.export_wikidata_review \
        --lexicon output/urdu_emergency_lexicon.ttl \
        --corpus data/sample_utterances.jsonl \
        --out output/wikidata_review.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import DCTERMS

# Same namespaces as src/ontolex_builder.py, declared here so this script
# only needs rdflib (not the Stanza/Whisper stack) to run.
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LEXINFO = Namespace("http://www.lexinfo.net/ontology/3.0/lexinfo#")

URDU_QID = "Q1617"
# Wikidata lexical-category items for the POS values this pipeline emits.
LEXICAL_CATEGORY_QID = {
    "noun": "Q1084",
    "properNoun": "Q147276",
    "verb": "Q24905",
    "adjective": "Q34698",
    "adverb": "Q380057",
}


def build_rows(lexicon_path: Path, corpus_path: Path) -> list[dict]:
    g = Graph()
    g.parse(lexicon_path, format="turtle")
    with corpus_path.open(encoding="utf-8") as f:
        corpus = {r["id"]: r for r in (json.loads(line) for line in f if line.strip())}

    rows = []
    for entry in g.subjects(predicate=ONTOLEX.canonicalForm):
        form = g.value(entry, ONTOLEX.canonicalForm)
        lemma = str(g.value(form, ONTOLEX.writtenRep))
        pos_uri = g.value(entry, LEXINFO.partOfSpeech)
        pos = str(pos_uri).rsplit("#", 1)[-1] if pos_uri else ""
        other = sorted(
            str(g.value(f, ONTOLEX.writtenRep))
            for f in g.objects(entry, ONTOLEX.otherForm)
        )
        sources = sorted(str(s) for s in g.objects(entry, DCTERMS.source))
        example = corpus.get(sources[0], {}) if sources else {}
        rows.append({
            "lemma": lemma,
            "pos": pos,
            "language_qid": URDU_QID,
            "lexical_category_qid": LEXICAL_CATEGORY_QID.get(pos, ""),
            "other_forms": " | ".join(other),
            "attestations": len(sources),
            "example_id": sources[0] if sources else "",
            "example_text": example.get("text", ""),
            "example_gloss": example.get("english_gloss", ""),
            "keep": "",
            "on_wikidata": "",
            "lexeme_id": "",
        })
    rows.sort(key=lambda r: (-r["attestations"], r["lemma"]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("--lexicon", type=Path, default=Path("output/urdu_emergency_lexicon.ttl"))
    parser.add_argument("--corpus", type=Path, default=Path("data/sample_utterances.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("output/wikidata_review.csv"))
    args = parser.parse_args()

    rows = build_rows(args.lexicon, args.corpus)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} entries to {args.out}")


if __name__ == "__main__":
    main()
