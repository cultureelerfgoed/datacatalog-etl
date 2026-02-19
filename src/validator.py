import os
import logging
import requests
from rdflib import Graph
from rdflib.namespace import RDF, SH

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
VALIDATION_API = 'https://datasetregister.netwerkdigitaalerfgoed.nl/api/datasets/validate'

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
    logger.info('Validation API <%s> response status code: %s', url, response.status_code)
    validationgraph = Graph()
    validationgraph.parse(data=response.text, format='application/ld+json')

    for subj, pred, obj in validationgraph.triples((None, RDF.type, SH.ValidationResult)):
        rpath = validationgraph.value(subj, SH.resultPath)
        rmsg = validationgraph.value(subj, SH.resultMessage)
        rval = validationgraph.value(subj, SH.focusNode)
        logger.info('<%s> %s <%s>', str(rpath), str(rmsg), str(rval))

    return validationgraph

def main():
    """ main runner for workflow """
    try:
        graph = Graph()
        graph.parse(source=TARGET_FILEPATH, format=OUTPUT_FILE_FORMAT)
        vgraph = validate(VALIDATION_API, graph)
        if vgraph.subjects(predicate=SH.resultSeverity, object=SH.Violation):
            logger.info('No Shacl violations found in datacatalog.')
            graph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)
            logger.info('Saved graph to %s (%s bytes)', TARGET_FILEPATH, os.path.getsize(TARGET_FILEPATH))
        else:
            logger.error('Invalid datacatalog, Shacl violations found.')
    except FileNotFoundError as fnfe:
        logger.warning('No allowlist found: %s', fnfe)
    
if __name__ == '__main__':
    main()
