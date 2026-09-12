"""
A genuine SPARQL HTTP endpoint over the generated OntoLex graph: loads a
serialized Turtle file into an rdflib Graph at startup and answers real
SPARQL queries over HTTP, rather than only supporting in-process
Graph.query() calls. Minimal by design (single-file graph, no auth, no
federation) — sufficient to make "queryable via SPARQL" a testable claim,
not a substitute for a production triple store (GraphDB, Fuseki) at scale.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from rdflib import Graph

GRAPH_PATH = os.getenv("ONTOLEX_GRAPH_PATH", "output/urdu_emergency_lexicon.ttl")

_graph = Graph()


def load_graph():
    if os.path.exists(GRAPH_PATH):
        _graph.parse(GRAPH_PATH, format="turtle")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_graph()
    yield


app = FastAPI(title="Urdu Emergency Lexicon SPARQL Endpoint", lifespan=lifespan)


@app.get("/sparql")
def sparql_query(query: str = Query(..., description="A SPARQL SELECT query")):
    try:
        results = _graph.query(query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid SPARQL query: {e}")

    return {
        "head": {"vars": [str(v) for v in results.vars]},
        "results": {
            "bindings": [
                {str(var): {"value": str(row[var])} for var in results.vars if row[var] is not None}
                for row in results
            ]
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "triples_loaded": len(_graph)}
