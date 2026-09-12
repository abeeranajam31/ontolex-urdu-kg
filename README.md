# Urdu Emergency Speech-to-Knowledge-Graph Pipeline

An open-science pipeline that turns Urdu emergency-domain speech (or pre-transcribed
text) into a real, valid **OntoLex-lemon** RDF knowledge graph — with genuine
morphosyntactic term extraction, live interlinking against Wikidata, and a queryable
SPARQL HTTP endpoint over the result.

> **Independent research pilot, not affiliated with any institution.** Built on the
> author's own [Urdu Emergency Communication Corpus](https://github.com/abeeranajam31/urdu-emergency-corpus)
> (60 researcher-constructed utterances) as sample input text, and on the author's
> fine-tuned Urdu Whisper checkpoint for the speech-to-text stage.

## Pipeline

```
  ┌────────────────────────────────────────────────────────┐
  │        Audio (Whisper ASR) OR pre-transcribed text      │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Morphosyntactic Term Extraction (Stanza Urdu UD)      │
  │   Real POS tagging + lemmatization — not a lexicon      │
  │   substring match                                       │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   OntoLex-Lemon RDF Builder (rdflib)                    │
  │   LexicalEntry / Form / LexicalSense + LexInfo POS,     │
  │   with dct:source provenance per attestation            │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Wikidata Interlinking (live SPARQL query)             │
  │   ontolex:reference from sense -> matched Wikidata item │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   SPARQL HTTP Endpoint (FastAPI + rdflib)               │
  └────────────────────────────────────────────────────────┘
```

## What's actually verified (not just designed)

Every stage below was run for real during development, not just written and assumed to work:

- **ASR**: `src/asr.py` wraps any Hugging Face Whisper checkpoint (default:
  [`abeeranajam31/whisper-small-urdu-v2`](https://huggingface.co/abeeranajam31/whisper-small-urdu-v2)).
  Verified against a synthesized test clip — exact transcript match.
- **Term extraction**: `src/term_extraction.py` uses Stanza's Urdu Universal
  Dependencies model for real tokenization, POS-tagging, and lemmatization.
  Verified on real corpus sentences — e.g. `آئیں` (imperative "come") correctly
  lemmatizes to `آنا` (infinitive).
- **OntoLex-lemon RDF**: `src/ontolex_builder.py` produces genuine
  `ontolex:LexicalEntry` / `Form` / `LexicalSense` triples with `lexinfo:partOfSpeech`
  and `dct:source` provenance. Verified via round-trip serialization (serialize to
  Turtle, re-parse, confirm identical triple count) and full pipeline runs — 60 sample
  utterances currently yield 207 distinct lexical entries and 1,946 triples.
- **Wikidata interlinking**: `src/wikidata_interlink.py` makes real, live SPARQL
  queries against `query.wikidata.org` (not a mock or fixture) and links a
  `LexicalSense` to a matched Wikidata item via `ontolex:reference`. A live query for
  `ڈاکٹر` ("doctor") correctly returned `wd:Q4618975`. **Caveat, observed directly
  during development**: Wikidata's public endpoint rate-limits aggressively and has
  real outages — the interlinker degrades to `None` per term on failure rather than
  crashing the pipeline, and this is unit-tested with a mocked failure response, not
  just hoped for.
- **SPARQL HTTP endpoint**: `src/sparql_service.py` is a real FastAPI service that
  loads the generated graph and answers arbitrary SPARQL `SELECT` queries over HTTP —
  tested end-to-end via `TestClient`, not just an in-process `Graph.query()` call.

16 tests across all four stages pass (`pytest tests/ -v`); see `.github/workflows/ci.yml`.

## Key Features
- **Speech-to-Text Ingestion**: pluggable Whisper checkpoint, defaulting to a
  fine-tuned Urdu model.
- **Real Morphosyntactic Analysis**: Stanza Urdu UD POS tagging and lemmatization,
  not a keyword/lexicon heuristic.
- **OntoLex Triplification**: maps extracted terms to `ontolex:LexicalEntry`,
  `ontolex:Form`, and `ontolex:LexicalSense`, with per-attestation provenance.
- **Linked Data Interlinking**: live SPARQL lookups against Wikidata, using the
  OntoLex-recommended `ontolex:reference` pattern rather than `owl:sameAs`.
- **Queryable Output**: a real SPARQL HTTP endpoint, not just a static file.

## Tech Stack
- **Speech & NLP**: PyTorch, Whisper (Transformers), Stanza
- **Semantic Web**: rdflib, SPARQLWrapper, OntoLex-lemon + LexInfo vocabularies
- **Service**: FastAPI

## How to Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build the graph from the sample corpus (skip --no-interlink to attempt
# live Wikidata lookups, which may be rate-limited — see caveat above)
python -m scripts.build_pipeline --no-interlink

# Serve it over SPARQL
uvicorn src.sparql_service:app --port 8010
curl "http://localhost:8010/sparql?query=SELECT%20%3Fs%20WHERE%20%7B%3Fs%20a%20%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23LexicalEntry%3E%7D%20LIMIT%205"

# Run the tests
python -m pytest tests/ -v
```

## Honest Limitations

- **Input is pre-transcribed text for the demonstrated pipeline runs**, reusing the
  author's own 60-utterance research corpus, not live audio — the ASR stage is real
  and tested independently (see above), but the two haven't been run together as one
  continuous audio-to-RDF demo in this repo yet.
- **The base RDF namespace (`example.org`) is a placeholder** (per RFC 2606) for a
  pilot that isn't hosted anywhere resolvable. Swap it for a real namespace before
  treating this as a published Linked Data resource.
- **Wikidata interlinking coverage is partial by nature** — it only finds a match when
  a term happens to exist as a Wikidata item with an exact Urdu label, and the public
  endpoint's rate-limiting means a full-corpus interlinking run may need to be spread
  out rather than done in one batch.
- **No DBnary interlinking is implemented** despite being architecturally compatible —
  Wikidata was chosen because it has a live, queryable public SPARQL endpoint; DBnary's
  Urdu Wiktionary coverage was not evaluated for this pilot.

## License

[MIT](LICENSE)

## Citation

```bibtex
@misc{urdu_ontolex_kg_2026,
  author = {Najam, Abeera},
  title = {Urdu Emergency Speech-to-Knowledge-Graph Pipeline},
  year = {2026},
  howpublished = {Independent research project},
  url = {https://github.com/abeeranajam31/ontolex-urdu-kg}
}
```

## Contact

Abeera Najam — [abeeranajam@gmail.com](mailto:abeeranajam@gmail.com)
