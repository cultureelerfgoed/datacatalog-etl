import os
import logging
import argparse
from typing import Tuple
import requests
from rdflib import Graph, Node
from rdflib.namespace import RDF, SH
import yaml

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')
ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'datacatalog.json-ld')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')

config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
logger = logging.getLogger(__name__)

def validate_url(url: str, expected_status: int):
    """ Validate URL against endpoint """
    logger.info('Testing PUT response from %s', url)
    datastr = '{ ' + f'"@id": "{url}"' + ' }'
    response = requests.put(config['VALIDATION_API'], headers={'accept': 'application/ld+json', 'Content-Type': 'application/ld+json'}, data=datastr, timeout=200)
    assert response.status_code == int(expected_status), f'Received status code {response.status_code}, expected {expected_status}, from {config['VALIDATION_API']}: {response.content}'

def validate_body(graph: Graph) -> Tuple[Graph, int]:
    """ Validate body against endpoint """
    strgraph = graph.serialize(format=OUTPUT_FILE_FORMAT, encoding=ENCODING)
    response = requests.post(config['VALIDATION_API'], headers={'accept': 'application/ld+json', 'Content-Type': 'application/ld+json'}, data=strgraph, timeout=200)
    #assert response.status_code == int(expected_status), f'Received status code {response.status_code}, expected {expected_status}, from {VALIDATION_API}..'
    validationgraph = Graph()
    validationgraph.parse(data=response.text, format='application/ld+json')
    return validationgraph, response.status_code

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
    parser = argparse.ArgumentParser(description='Datacatalog validation')
    parser.add_argument('-m','--method', help='Request method', required=True)
    parser.add_argument('-s','--status', help='Expected status code', required=True)
    args = vars(parser.parse_args())
    if str.upper(args['method']) == 'GET':
        tgraph = Graph()
        tgraph.parse(ARTIFACT_PATH, format=OUTPUT_FILE_FORMAT, encoding=ENCODING)
        expected_status = int(args['status'])
        vgraph, rstatus = validate_body(tgraph)
        
        for subj, pred, obj in vgraph.triples((None, RDF.type, SH.ValidationResult)):
            if vgraph.value(subj, SH.resultSeverity) == SH.Info:
                logger.info(get_logstring(tgraph, vgraph, subj))                
            elif vgraph.value(subj, SH.resultSeverity) == SH.Warning:
                logger.warning(get_logstring(tgraph, vgraph, subj))
            elif vgraph.value(subj, SH.resultSeverity) == SH.Violation:
                logger.error('Invalid datacatalog, Shacl violations found.')
                logger.error(get_logstring(tgraph, vgraph, subj))
                raise ValueError(f'Failed Shacl validation: {str(vgraph.value(subj, SH.focusNode))}')
            
        assert rstatus == expected_status, f'Received status code {rstatus}, expected {expected_status}, from {config['VALIDATION_API']}..'
    elif str.upper(args['method']) == 'PUT':
        validate_url(args['url'], args['status'])

if __name__ == '__main__':
    main()
