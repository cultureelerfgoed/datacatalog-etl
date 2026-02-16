import json
import os
import logging
import requests
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO, SH

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
BASE_URI = os.getenv('BASE_URI', 'https://kennis.cultureelerfgoed.nl/api.php')
ENCODING = os.getenv('ENCODING', 'utf-8')
ALLOWLIST_PATH = os.getenv('ALLOWLIST_PATH', 'allowlist.jsonld')

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# --- Get query response from URI ---
def get_mwquery_response_as_json(from_url: str, query: str) -> any:
    get_params = {
        'action': 'ask',
        'query': query,
        'format': 'json'
    }
    response = requests.get(from_url, params=get_params, timeout=100)
    logger.info('Query response from %s received', from_url)
    return json.loads(response.text)

# --- Return graph from JSON dict  ---
def parse_json_to_graph(dc_json: dict, graph_id: str, allowlist: Graph) -> Graph:
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
    
    # datacatalog definition
    datacatalog_node = URIRef('https://linkeddata.cultureelerfgoed.nl/rce/datacatalog-rce/')
    graph.add((datacatalog_node, RDF.type, SDO.DataCatalog))
    graph.add((datacatalog_node, SDO.name, Literal('RCE Datacatalogus', lang='nl')))
    graph.add((datacatalog_node, SDO.publisher, organization_node))

    for result in dc_json['query']['results']:
        # dataset definition
        dataset_node = URIRef(dc_json['query']['results'][result]['fullurl'])
        if (dataset_node, RDF.type, SDO.DataDownload) in allowlist:
            logger.info('Found dataset %s in allowlist.', str(dataset_node))
            dataset_properties = dc_json['query']['results'][result]['printouts']
            ds_name = Literal(dataset_properties['Naam'][0], lang='nl')
            ds_description = Literal(dataset_properties['Omschrijving'][0], lang='nl')
            ds_genre = Literal(dataset_properties['Dataset rubriek'][0], lang='nl')
            ds_license = URIRef('https://creativecommons.org/licenses/by/4.0/')
            ds_domain = Literal(dataset_properties['Dataset domein'][0], lang='nl')
            ds_encoding = Literal('application/sparql-results+xml')
            ds_contentURL = URIRef(allowlist.value(dataset_node, SDO.contentUrl) or dataset_properties['Bronurl'][0])

            if 'Nee' or 'Geen' in dataset_properties['Dataset beperkingen']:
                graph.add((dataset_node, SDO.license, ds_license))
            else: 
                logger.info('No License: %s', dataset_properties['Dataset beperkingen'])

            graph.add((dataset_node, RDF.type, SDO.Dataset))
            graph.add((dataset_node, SDO.name, ds_name))
            graph.add((dataset_node, SDO.publisher, organization_node))
            graph.add((dataset_node, SDO.description, ds_description))
            graph.add((dataset_node, SDO.genre, ds_genre))

            if 'Alle' not in dataset_properties['Dataset domein'][0]:
                graph.add((dataset_node, SDO.keywords, ds_domain))

            graph.remove((dataset_node, None, Literal('')))
            dl_distribution_node = URIRef(dataset_properties['Bronurl'][0])
            graph.add((dl_distribution_node, RDF.type, SDO.DataDownload))
            graph.add((dl_distribution_node, SDO.encodingFormat, ds_encoding))
            graph.add((dl_distribution_node, SDO.contentUrl, ds_contentURL))
            graph.add((dataset_node, SDO.distribution, dl_distribution_node))
            graph.add((datacatalog_node, SDO.dataset, dataset_node))

    return graph

def validate(url: str, graph: Graph) -> any:
    headers = {
        'accept': 'application/ld+json',
        'Content-Type': 'application/ld+json'}
    strgraph = graph.serialize(format=OUTPUT_FILE_FORMAT)
    response = requests.post(url, headers=headers, data=strgraph, timeout=100)

    logger.info('Validation API <%s> response status code: %s', url, response.status_code)
    validationgraph = Graph()
    validationgraph.parse(data=response.text, format='application/ld+json')
    logger.info('validationgraph length: %i', len(validationgraph))

    for subj, pred, obj in validationgraph.triples((None, RDF.type, SH.ValidationResult)):
        rpath = validationgraph.value(subj, SH.resultPath)
        rmsg = validationgraph.value(subj, SH.resultMessage)
        rval = validationgraph.value(subj, SH.focusNode)
        rsev = validationgraph.value(subj, SH.resultSeverity)
        logger.info('<%s> %s:%s <%s>', str(rpath), str(rsev.n3), str(rmsg), str(rval))

    return validationgraph

def main():
    try:
        datacatalog_json = get_mwquery_response_as_json('https://kennis.cultureelerfgoed.nl/api.php', '[[Categorie:Datasets]]|limit=500|?Status|?Batch|?Naam|?Dataset type|?Omschrijving|?Zichtbaar in Erfgoedatlas|?Dataset|?Bronurl|?Dataset creatie|?Dataset domein|?Dataset rubriek|?Dataset beperkingen')
        with open('kb_datacatalog.json', 'w') as file:
            json.dump(datacatalog_json, file)
        allowlist = Graph()
        allowlist.parse(ALLOWLIST_PATH)
        graph = parse_json_to_graph(datacatalog_json, GRAPH_ID, allowlist)
        graph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)  
        logger.info('Saved graph to %s (%s bytes)', TARGET_FILEPATH, os.path.getsize(TARGET_FILEPATH))  
        vgraph = validate('https://datasetregister.netwerkdigitaalerfgoed.nl/api/datasets/validate', graph)
        if SH.Violation not in vgraph:
            graph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)  
            logger.info('Saved graph to %s (%s bytes)', TARGET_FILEPATH, os.path.getsize(TARGET_FILEPATH))  
    except FileNotFoundError as fnfe:
        logger.warning('No allowlist found: %s', fnfe)

if __name__ == '__main__':
    main()