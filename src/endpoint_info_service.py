import json
from datetime import datetime
import requests
from rdflib import Graph, Node, Literal, URIRef
from rdflib.namespace import SDO, XSD
from static import LICENSES, KEYWORD_TERMS

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
    
    for tag in item.get('tags'):
        if(KEYWORD_TERMS.get(tag)):
            graph.add((dataset_node, SDO.about, URIRef(KEYWORD_TERMS.get(tag))))

    graph.add((dataset_node, SDO.license, URIRef(LICENSES[item.get('license', 'default')])))
    graph.add((dataset_node, SDO.dateCreated, Literal(created.date().isoformat(), datatype=XSD.date)))
    graph.add((dataset_node, SDO.dateModified, Literal(modified.date().isoformat(), datatype=XSD.date)))
    graph.add((dataset_node, SDO.datePublished, Literal(published.date().isoformat(), datatype=XSD.date)))
    graph.add((distribution_node, SDO.dateCreated, Literal(created.date().isoformat(), datatype=XSD.date)))
    graph.add((distribution_node, SDO.dateModified, Literal(modified.date().isoformat(), datatype=XSD.date)))
    #graph.add((distribution_node, SDO.inLanguage, Literal('nl-NL', datatype=XSD.language)))
    #graph.add((distribution_node, SDO.inLanguage, Literal('en-US', datatype=XSD.language)))
    graph.add((dataset_node, SDO.inLanguage, Literal('nl-NL', datatype=XSD.language)))
    return graph