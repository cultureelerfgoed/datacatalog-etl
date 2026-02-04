import requests
import json
import os
import logging
import typing
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, DCAT, RDF

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'ttl')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.ttl')
BASE_URI = os.getenv('BASE_URI', 'https://kennis.cultureelerfgoed.nl/api.php')
ENCODING = os.getenv('ENCODING', 'utf-8')

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# --- Save graph to file ---
def save_graph(graph: Graph, filepath: str, format: str) -> None:
    """Save RDF graph to file."""
    graph.serialize(
        format=format,
        destination=filepath,
        encoding=ENCODING,
        auto_compact=True
    )
    logger.info(f'Saved graph to {filepath} ({os.path.getsize(filepath)} bytes)')

# --- Get query response from URI ---
def get_query_response(from_url: str, query: str) -> Any:
    get_params = {
        'action': 'ask',
        'query': query,
        'format': 'json'
    }
    response = requests.get(from_url, params=get_params, timeout=100)
    logger.info(f'Query response from {from_url} received')
    return json.loads(response.text)

# --- Return graph from JSON dict  ---
def parse_json_to_graph(dc_json: Dict, graph_id: str) -> Graph:
    graph = Graph(identifier=graph_id)

    for result in dc_json['query']['results']:
            dataset_node = URIRef(dc_json['query']['results'][result]['fullurl'])
            dataset_properties = dc_json['query']['results'][result]['printouts']
            graph.add((dataset_node, RDF.type, DCAT.dataset))
            graph.add((dataset_node, DCTERMS.title, Literal(dataset_properties['Naam'])))
            graph.add((dataset_node, DCTERMS.description, Literal(dataset_properties['Omschrijving'])))
            graph.add((dataset_node, DCAT.mediaType, Literal(dataset_properties['Dataset type'])))

    return graph

def main():
    datacatalog_json = get_query_response(BASE_URI, '[[Categorie:Datasets]]|limit=500|?Status|?Batch|?Naam|?Dataset type|?Omschrijving|?Zichtbaar in Erfgoedatlas|?Dataset|?Bronurl|?Dataset creatie|?Dataset domein|?Dataset rubriek|?Dataset beperkingen')
    #with open('datacatalog.json') as f:
    #    datacatalog_json = json.load(f)
    graph = parse_json_to_graph(datacatalog_json, GRAPH_ID)
    save_graph(graph, TARGET_FILEPATH, OUTPUT_FILE_FORMAT)        

if __name__ == '__main__':
    main()