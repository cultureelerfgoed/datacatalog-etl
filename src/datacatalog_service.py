import json
import os
import logging
from typing import Iterable
from urllib.parse import urlsplit
import requests
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO
import endpoint_info_service
import config
from config import KENNISBANK_MAPPING as MAPPING

logger = logging.getLogger(__name__)

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

def get_organization() -> Graph:
    graph = Graph(identifier=config.GRAPH_ID)
    # organization information
    organization_node = URIRef(config.ORG_URI)
    graph.add((organization_node, RDF.type, SDO.Organization))
    graph.add((organization_node, SDO.name, Literal(config.ORG_NAME, lang='nl')))
    graph.add((organization_node, SDO.sameAs, URIRef(config.ORG_SAME_AS)))
    cp_node = BNode()
    graph.add((cp_node, RDF.type, SDO.ContactPoint))
    graph.add((cp_node, SDO.name, Literal(config.ORG_CONTACT_NAME, lang='nl')))
    graph.add((cp_node, SDO.email, Literal(config.ORG_CONTACT_EMAIL)))
    graph.add((organization_node, SDO.contactPoint, cp_node))
    graph.add((organization_node, SDO.identifier, Literal(config.ORG_ISIL)))
    graph.add((organization_node, SDO.alternateName, Literal(config.ORG_ALTNAME, lang='en')))
    return graph

def parse_json_to_graph(dc_json: dict, graph_id: str) -> Graph:
    """ Return graph from query response as JSON dict """

    graph = get_organization()

    for result in dc_json['query']['results']:
        if dc_json['query']['results'][result]['printouts'][config.KENNISBANK_ENDPOINT]:
            
            # dataset definition
            furl = dc_json['query']['results'][result]['fullurl']
            durl = f'https://linkeddata.cultureelerfgoed.nl/rce/datacatalog/{urlsplit(furl).path[11:]}'
            dataset_node = URIRef(durl)
            dataset_properties = dc_json['query']['results'][result]['printouts']
            endpoint = dataset_properties[config.KENNISBANK_ENDPOINT][0]

            if any(word in dataset_properties[config.KENNISBANK_BEPERKINGEN][0] for word in ['Nee', 'Geen']):
                logger.info('Found dataset: %s with endpoint: %s', str(dataset_node), endpoint)
                graph.add((dataset_node, RDF.type, SDO.Dataset))
                graph.add((dataset_node, SDO.publisher, URIRef(config.ORG_URI)))
                
                graph.add((dataset_node, MAPPING[config.KENNISBANK_NAAM], get_literal_from_mw_response(dataset_properties, config.KENNISBANK_NAAM)))
                graph.add((dataset_node, MAPPING[config.KENNISBANK_OMSCHRIJVING], get_literal_from_mw_response(dataset_properties, config.KENNISBANK_OMSCHRIJVING)))
                graph.add((dataset_node, MAPPING[config.KENNISBANK_RUBRIEK], get_literal_from_mw_response(dataset_properties, config.KENNISBANK_RUBRIEK)))

                if 'Alle' not in dataset_properties[config.KENNISBANK_DOMEIN][0]:
                    spl_tags = try_safe_split_by_str(dataset_properties[config.KENNISBANK_DOMEIN][0], ';')
                    for keyword in spl_tags:
                        graph.add((dataset_node, SDO.keywords, Literal(keyword, lang='nl')))
                else:
                    graph.add((dataset_node, SDO.keywords, Literal('Monumenten', lang='nl')))
                    graph.add((dataset_node, SDO.keywords, Literal('Landschap', lang='nl')))
                    graph.add((dataset_node, SDO.keywords, Literal('Kunstcollecties', lang='nl')))
                    graph.add((dataset_node, SDO.keywords, Literal('Archeologie', lang='nl')))
                    graph.add((dataset_node, SDO.keywords, Literal('Gebouwd', lang='nl')))
                    graph.add((dataset_node, SDO.keywords, Literal('Roerend', lang='nl')))

                graph.remove((dataset_node, None, Literal('')))
                dl_distribution_node = BNode()
                graph.add((dl_distribution_node, RDF.type, SDO.DataDownload))
                graph.add((dl_distribution_node, SDO.encodingFormat, Literal('application/sparql-results+xml')))
                endpoint = URIRef(dc_json['query']['results'][result]['printouts'][config.KENNISBANK_ENDPOINT][0])
                graph.add((dl_distribution_node, SDO.contentUrl, endpoint))
                graph.add((dl_distribution_node, SDO.description, Literal(f'Sparql-endpoint van {dataset_properties[config.KENNISBANK_NAAM][0]} op de Linked-Data Voorziening van de RCE.')))
                graph.add((dataset_node, SDO.distribution, dl_distribution_node))
                graph.add((dataset_node, SDO.creator, URIRef(config.ORG_URI)))
                meta_graph = endpoint_info_service.get_dataset_metadata(str(endpoint), dataset_node, dl_distribution_node)
                graph = graph + meta_graph
            
    return graph

def try_safe_split_by_str(val: str, delimiter: str) -> Iterable[str]:
    """ Method to delimit strings without raising an error """ 
    try:
        return filter(lambda c: c.isalnum(), val.split(delimiter))
    except BaseException:
        return {val}
    
def get_literal_from_mw_response(response: dict, fieldname: str, lang='nl') -> Literal:
    return Literal(response[fieldname][0], lang)

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    try:
        datacatalog_json = get_mwquery_response_as_json(config.SRC_URI, config.KB_DC_QUERY)
        with open('kb_datacatalog.json', 'w', encoding=config.ENCODING) as file:
            json.dump(datacatalog_json, file)
        graph = parse_json_to_graph(datacatalog_json, config.GRAPH_ID)
        logger.info("Writing  %s", f"{config.OUTPUT_FILE_FORMAT} file to {config.TARGET_FILEPATH}")
        graph.serialize(format=config.OUTPUT_FILE_FORMAT, destination=config.TARGET_FILEPATH, encoding=config.ENCODING, auto_compact=True)  
        logger.info("Filesize:  %s", f"{os.path.getsize(config.TARGET_FILEPATH)} bytes")
    except OSError as oe:
        logger.warning('Failed to write datacatalog from Kennisbank to file: %s', oe)

if __name__ == '__main__':
    main()
