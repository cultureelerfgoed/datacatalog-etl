import json
import os
import logging
from datetime import datetime
from urllib.parse import urlsplit
import requests
from rdflib import Graph, Node, Literal, BNode, URIRef
from rdflib.namespace import SDO
import config

logger = logging.getLogger(__name__)

def get_dataset_uri(accountname: str, datasetname: str):
    """ return uri of dataset based on base uri, accountname, and datasetname """    
    return f'https://api.{urlsplit(config.BASE_URI).hostname}/datasets/{accountname}/{datasetname}/'

def get_dataset_uri_by_endpoint(endpoint: str):
    """ Return uri of dataset based on uri of endpoint  """
    return endpoint.removesuffix('sparql')

def get_dataset_metadata(q_url: str, dataset_node: Node, distribution_node: Node) -> Graph:
    """ Validate against endpoint """
    headers = {'accept': 'text/plain'}
    response = requests.get(get_dataset_uri_by_endpoint(q_url), headers=headers, timeout=100)
    item = json.loads(response.content)
    graph = Graph()
    timeformat_src = '%Y-%m-%dT%H:%M:%S.%fZ'
    created = datetime.strptime(item.get('createdAt'), timeformat_src)
    modified = datetime.strptime(item.get('updatedAt'), timeformat_src)
    published = datetime.strptime(item.get('lastGraphsUpdateTime'), timeformat_src)
    graph.add((dataset_node, SDO.license, URIRef(config.LICENSES[item.get('license', config.LICENSES['default'])])))
    graph.add((dataset_node, SDO.dateCreated, Literal(created.date().isoformat())))
    graph.add((dataset_node, SDO.dateModified, Literal(modified.date().isoformat())))
    graph.add((dataset_node, SDO.datePublished, Literal(published.date().isoformat())))
    graph.add((distribution_node, SDO.dateCreated, Literal(created.date().isoformat())))
    graph.add((distribution_node, SDO.dateModified, Literal(modified.date().isoformat())))
    graph.add((distribution_node, SDO.inLanguage, Literal('nl')))
    graph.add((distribution_node, SDO.inLanguage, Literal('en')))
    return graph