import json
import os
import logging
import requests
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
SRC_URI = os.getenv('SRC_URI', 'https://kennis.cultureelerfgoed.nl/api.php')
ENCODING = os.getenv('ENCODING', 'utf-8')
ALLOWLIST_PATH = os.getenv('ALLOWLIST_PATH', 'allowlist.jsonld')

KB_DC_QUERY = '[[Categorie:Datasets]]|limit=500|?Status|?Batch|?Naam|?Dataset type|?Omschrijving' \
'|?Zichtbaar in Erfgoedatlas|?Dataset|?Bronurl|?Dataset creatie|?Dataset domein|?Dataset rubriek|?Dataset beperkingen'

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def get_mwquery_response_as_json(from_url: str, query: str):
    """ Get query response from URI """
    get_params = {
        'action': 'ask',
        'query': query,
        'format': 'json'
    }
    response = requests.get(from_url, params=get_params, timeout=100)
    logger.info('Query response from %s received', from_url)
    return json.loads(response.text)

def parse_json_to_graph(dc_json: dict, graph_id: str, allowlist: Graph) -> Graph:
    """ Return graph from query response as JSON dict """

    graph = Graph(identifier=graph_id)

    # organization information
    organization_node = URIRef('https://www.cultureelerfgoed.nl')
    graph.add((organization_node, RDF.type, SDO.Organization))
    graph.add((organization_node, SDO.name, Literal('Rijksdienst voor het Cultureel Erfgoed', lang='nl')))
    graph.add((organization_node, SDO.sameAs, URIRef('https://standaarden.overheid.nl/owms/terms/Rijksdienst_voor_het_Cultureel_Erfgoed')))
    cp_node = BNode()
    graph.add((cp_node, RDF.type, SDO.ContactPoint))
    graph.add((cp_node, SDO.name, Literal('Infodesk van de RCE', lang='nl')))
    graph.add((cp_node, SDO.email, Literal('info@cultureelerfgoed.nl')))
    graph.add((organization_node, SDO.contactPoint, cp_node))
    graph.add((organization_node, SDO.identifier, Literal('NL-AmfRCE')))
    graph.add((organization_node, SDO.alternateName, Literal('Cultural Heritage Agency of the Netherlands', lang='en')))

    for result in dc_json['query']['results']:
        # dataset definition
        dataset_node = URIRef(dc_json['query']['results'][result]['fullurl'])
        dataset_properties = dc_json['query']['results'][result]['printouts']

        #if any(word in 'some one long two phrase three' for word in list_):
        if (dataset_node, RDF.type, SDO.DataDownload) in allowlist and any(word in dataset_properties['Dataset beperkingen'][0] for word in ['Nee', 'Geen']):
            logger.info('Found dataset %s in allowlist.', str(dataset_node))
            graph.add((dataset_node, RDF.type, SDO.Dataset))
            graph.add((dataset_node, SDO.name, Literal(dataset_properties['Naam'][0], lang='nl')))
            graph.add((dataset_node, SDO.publisher, organization_node))
            graph.add((dataset_node, SDO.description, Literal(dataset_properties['Omschrijving'][0], lang='nl')))
            graph.add((dataset_node, SDO.genre, Literal(dataset_properties['Dataset rubriek'][0], lang='nl')))
            graph.add((dataset_node, SDO.license, URIRef('https://creativecommons.org/licenses/by/4.0/')))

            if 'Alle' not in dataset_properties['Dataset domein'][0]:
                graph.add((dataset_node, SDO.keywords, Literal(dataset_properties['Dataset domein'][0], lang='nl')))
            else:
                graph.add((dataset_node, SDO.keywords, Literal('Monumenten; Landschap; Kunstcollecties; Archeologie; Gebouwd; Roerend', lang='nl')))

            graph.remove((dataset_node, None, Literal('')))
            dl_distribution_node = BNode()
            graph.add((dl_distribution_node, RDF.type, SDO.DataDownload))
            graph.add((dl_distribution_node, SDO.encodingFormat, Literal('application/sparql-results+xml')))
            graph.add((dl_distribution_node, SDO.contentUrl, URIRef(str(allowlist.value(dataset_node, SDO.contentUrl) or dataset_properties['Bronurl'][0]))))
            graph.add((dl_distribution_node, SDO.description, graph.value(dataset_node, SDO.description)))
            graph.add((dataset_node, SDO.distribution, dl_distribution_node))
            
    return graph

def main():
    """ main runner for workflow """
    try:
        datacatalog_json = get_mwquery_response_as_json(SRC_URI, KB_DC_QUERY)
        with open('kb_datacatalog.json', 'w', encoding=ENCODING) as file:
            json.dump(datacatalog_json, file)
        allowlist = Graph()
        allowlist.parse(ALLOWLIST_PATH)
        for s, p, o in allowlist.triples((None, SDO.contentUrl, None)):
            logger.info('%s: %s', str(s), str(o))
        graph = parse_json_to_graph(datacatalog_json, GRAPH_ID, allowlist)
        graph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)  
    except OSError as oe:
        logger.warning('Failed to write datacatalog from Kennisbank to file: %s', oe)

if __name__ == '__main__':
    main()