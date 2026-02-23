import os
import logging
import requests
from rdflib import Graph, Node
from rdflib.namespace import RDF, SH

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
VALIDATION_API = os.getenv('VALIDATION_API', 'https://datasetregister.netwerkdigitaalerfgoed.nl/api/datasets/validate')

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def validate(url: str, graph: Graph) -> Graph:
    """ Validate against endpoint """
    headers = {
        'accept': 'application/ld+json',
        'Content-Type': 'application/ld+json'}
    strgraph = graph.serialize(format=OUTPUT_FILE_FORMAT)
    response = requests.post(url, headers=headers, data=strgraph, timeout=100)
    
    if response.status_code == 200:
        logger.info('Validation API <%s> response status code: %s', url, response.status_code)
    elif response.status_code == 400:
        logger.error('Validation API <%s> response status code: %s', url, response.status_code)

    validationgraph = Graph()
    validationgraph.parse(data=response.text, format='application/ld+json')
    return validationgraph

def get_logstring(targetgraph: Graph, validationgraph: Graph, subject_node: Node):
    rmsg = validationgraph.value(subject_node, SH.resultMessage)
    fnode = validationgraph.value(subject_node, SH.focusNode)
    fnode_type = targetgraph.value(fnode, RDF.type)
    return f'{str(fnode_type)}: {str(rmsg)}'

def main():
    """ main runner for workflow """
    tgraph = Graph()
    tgraph.parse(source=TARGET_FILEPATH, format=OUTPUT_FILE_FORMAT)
    vgraph = validate(VALIDATION_API, tgraph)
    
    for subj, pred, obj in vgraph.triples((None, RDF.type, SH.ValidationResult)):
        if vgraph.value(subj, SH.resultSeverity) == SH.Info:
            logger.info(get_logstring(tgraph, vgraph, subj))                
        elif vgraph.value(subj, SH.resultSeverity) == SH.Warning:
            logger.warning(get_logstring(tgraph, vgraph, subj))
        elif vgraph.value(subj, SH.resultSeverity) == SH.Violation:
            logger.error('Invalid datacatalog, Shacl violations found.')
            logger.error(get_logstring(tgraph, vgraph, subj))
            raise ValueError(f'Failed Shacl validation: {str(vgraph.value(subj, SH.focusNode))}')
    
if __name__ == '__main__':
    main()
