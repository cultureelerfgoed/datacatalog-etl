import json
import os
import logging
from datetime import datetime
from urllib.parse import urlsplit
import requests
from rdflib import Graph, Node, Literal, BNode
from rdflib.namespace import SDO

ENCODING = os.getenv('ENCODING', 'utf-8')
BASE_URI = os.getenv('BASE_URI', 'https://linkeddata.cultureelerfgoed.nl/')
ACCOUNTS = {'rce', 'thesauri'}

logger = logging.getLogger(__name__)

def get_dataset_uri(accountname: str, datasetname: str):
    """ return uri of dataset based on base uri, accountname, and datasetname """    
    return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/{datasetname}/'

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
    timeformat_tgt = '%Y-%m-%d'
    created = datetime.strptime(item.get('createdAt'), timeformat_src)
    modified = datetime.strptime(item.get('updatedAt'), timeformat_src)
    graph.add((dataset_node, SDO.dateCreated, Literal(datetime.strftime(created, timeformat_tgt))))
    graph.add((dataset_node, SDO.dateModified, Literal(datetime.strftime(modified, timeformat_tgt))))
    graph.add((distribution_node, SDO.dateCreated, Literal(datetime.strftime(created, timeformat_tgt))))
    graph.add((distribution_node, SDO.dateModified, Literal(datetime.strftime(modified, timeformat_tgt))))
    graph.add((distribution_node, SDO.inLanguage, Literal('nl')))
    graph.add((distribution_node, SDO.inLanguage, Literal('en')))
    return graph

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    g = get_dataset_metadata('https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/datacatalog/sparql', BNode(), BNode())
    g.print()
    
if __name__ == '__main__':
    main()