import json
import os
import logging
import requests
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, DCAT, RDF, PROV

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
BASE_URI = os.getenv('BASE_URI', 'https://kennis.cultureelerfgoed.nl/api.php')
ENCODING = os.getenv('ENCODING', 'utf-8')
WHITELIST_PATH = os.getenv('WHITELIST_PATH', 'whitelist.jsonld')

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# --- Save graph to file ---
def save_graph(graph: Graph, filepath: str, fileformat: str) -> None:
    """Save RDF graph to file."""
    graph.serialize(
        format=fileformat,
        destination=filepath,
        encoding=ENCODING,
        auto_compact=True
    )
    logger.info('Saved graph to %s (%s bytes)', filepath, os.path.getsize(filepath))


# --- Get query response from URI ---
def get_query_response(from_url: str, query: str) -> any:
    get_params = {
        'action': 'ask',
        'query': query,
        'format': 'json'
    }
    response = requests.get(from_url, params=get_params, timeout=100)
    logger.info('Query response from %s received', from_url)
    return json.loads(response.text)

# --- Return graph from JSON dict  ---
def parse_json_to_graph(dc_json: dict, graph_id: str, whitelist: Graph=None) -> Graph:
    graph = Graph(identifier=graph_id)

    # datacatalog definition
    datacatalog_node = URIRef('https://linkeddata.cultureelerfgoed.nl/rce/datacatalog-rce/')
    graph.add((datacatalog_node, RDF.type, DCAT.catalog))
    graph.add((datacatalog_node, DCAT.contactPoint, Literal('thesauri@cultureelerfgoed.nl')))
    graph.add((datacatalog_node, DCTERMS.description,Literal('RCE Datalog of datasets')))
    graph.add((datacatalog_node, DCTERMS.publisher, Literal('https://linkeddata.cultureelerfgoed.nl/')))
    graph.add((datacatalog_node, DCTERMS.title, Literal('RCE Datacatalog')))

    
    for result in dc_json['query']['results']:
        # dataset definition
        dataset_node = URIRef(dc_json['query']['results'][result]['fullurl'])
        dataset_properties = dc_json['query']['results'][result]['printouts']
        graph.add((dataset_node, RDF.type, DCAT.Dataset))
        graph.add((dataset_node, DCTERMS.title, Literal(dataset_properties['Naam'][0])))
        graph.add((dataset_node, DCTERMS.description, Literal(dataset_properties['Omschrijving'][0])))
        graph.add((dataset_node, DCAT.theme, Literal(dataset_properties['Dataset type'][0])))
        graph.add((dataset_node, DCTERMS.publisher, URIRef('https://data.cultureelerfgoed.nl/term/id/cht/1576adc6-1af1-44d0-9d46-593eb6bcad09')))
        graph.add((dataset_node, DCAT.servesDataset, URIRef('https://linkeddata.cultureelerfgoed.nl/datacatalog-rce')))
        graph.add((dataset_node, DCAT.keyword, Literal(dataset_properties['Dataset domein'][0])))
        graph.add((dataset_node, PROV.wasGeneratedBy, Literal(dataset_properties['Dataset creatie'][0])))
        graph.add((dataset_node, DCAT.landingPage, URIRef(dc_json['query']['results'][result]['fullurl'])))
        
        # distribution definition
        distribution_node = BNode()
        graph.add((distribution_node, RDF.type, DCAT.Distribution))
        graph.add((distribution_node, DCAT.downloadURL, URIRef(dataset_properties['Bronurl'][0])))
        graph.add((dataset_node, DCAT.distribution, distribution_node))

        # access URL uit config?
        if (dataset_node, RDF.type, DCAT.Dataset) in whitelist:
            logger.info('Found accessURL entry in whitelist.')
            #graph.add((distribution_node, DCAT.accessURL, whitelist.get ?

        if 'Ja' in dataset_properties['Zichtbaar in Erfgoedatlas']: 
            graph.add((dataset_node, DCTERMS.isReferencedBy, URIRef('https://rce.webgis.nl/nl/map/erfgoedatlas')))
        graph.add((dataset_node, DCAT.keyword, Literal(dataset_properties['Dataset rubriek'][0])))
        if 'Nee' in dataset_properties['Dataset beperkingen']:
            graph.add((dataset_node, DCTERMS.accessRights, URIRef('https://creativecommons.org/licenses/by/4.0/')))
        graph.remove((dataset_node, None, Literal('[]')))
        graph.add((datacatalog_node, DCAT.dataset, dataset_node))
        #"cc-by4.0"
    return graph

def main():
    datacatalog_json = get_query_response(BASE_URI, '[[Categorie:Datasets]]|limit=500|?Status|?Batch|?Naam|?Dataset type|?Omschrijving|?Zichtbaar in Erfgoedatlas|?Dataset|?Bronurl|?Dataset creatie|?Dataset domein|?Dataset rubriek|?Dataset beperkingen')
    
    try:
        whitelist = Graph()
        whitelist.parse(WHITELIST_PATH)
        graph = parse_json_to_graph(datacatalog_json, GRAPH_ID)
        save_graph(graph, TARGET_FILEPATH, OUTPUT_FILE_FORMAT)
    except FileNotFoundError as fnfe:
        logger.warning('No whitelist found: %s', fnfe)

if __name__ == '__main__':
    main()