import os
import logging
import argparse
import requests
from rdflib import Graph, Node
from rdflib.namespace import RDF, SH

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
VALIDATION_API = os.getenv('VALIDATION_API', 'https://datasetregister.netwerkdigitaalerfgoed.nl/api/datasets/validate')

logger = logging.getLogger(__name__)

def validate_url(url: str, expected_status: int):
    """ Validate URL against endpoint """
    logger.info('Testing PUT response from %s', url)
    datastr = '{ ' + f'"@id": "{url}"' + ' }'
    response = requests.put(VALIDATION_API, headers={'accept': 'application/ld+json', 'Content-Type': 'application/ld+json'}, data=datastr, timeout=200)
    assert response.status_code == int(expected_status), f'Received status code {response.status_code}, expected {expected_status}, from {VALIDATION_API}: {response.content}'

def validate_body(graph: Graph, expected_status: int) -> Graph:
    """ Validate body against endpoint """
    strgraph = graph.serialize(format=OUTPUT_FILE_FORMAT)
    response = requests.post(VALIDATION_API, headers={'accept': 'application/ld+json', 'Content-Type': 'application/ld+json'}, data=strgraph, timeout=200)
    assert response.status_code == int(expected_status), f'Received status code {response.status_code}, expected {expected_status}, from {VALIDATION_API}..'
    validationgraph = Graph()
    validationgraph.parse(data=response.text, format='application/ld+json')
    return validationgraph

def get_logstring(targetgraph: Graph, validationgraph: Graph, subject_node: Node):
    """ Format Shacl validation as nice string """
    rmsg = validationgraph.value(subject_node, SH.resultMessage)
    fnode = validationgraph.value(subject_node, SH.focusNode)
    fnode_type = targetgraph.value(fnode, RDF.type)
    return f'{str(fnode_type)}: {str(rmsg)}'

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser(description='PoolParty tests')
    parser.add_argument('-u','--url', help='Target URL', required=False)
    parser.add_argument('-p','--path', help='Target path', required=False)
    parser.add_argument('-m','--method', help='Request method', required=True)
    parser.add_argument('-s','--status', help='Expected status code', required=True)
    args = vars(parser.parse_args())
    if str.upper(args['method']) == 'GET':
        tgraph = Graph()
        tgraph.parse(args['path'], format=OUTPUT_FILE_FORMAT)
        vgraph = validate_body(tgraph, args['status'])
        
        for subj, pred, obj in vgraph.triples((None, RDF.type, SH.ValidationResult)):
            if vgraph.value(subj, SH.resultSeverity) == SH.Info:
                logger.info(get_logstring(tgraph, vgraph, subj))                
            elif vgraph.value(subj, SH.resultSeverity) == SH.Warning:
                logger.warning(get_logstring(tgraph, vgraph, subj))
            elif vgraph.value(subj, SH.resultSeverity) == SH.Violation:
                logger.error('Invalid datacatalog, Shacl violations found.')
                logger.error(get_logstring(tgraph, vgraph, subj))
                raise ValueError(f'Failed Shacl validation: {str(vgraph.value(subj, SH.focusNode))}')
    elif str.upper(args['method']) == 'PUT':
        validate_url(args['url'], args['status'])

if __name__ == '__main__':
    main()
