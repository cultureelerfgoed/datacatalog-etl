import os
import logging
import requests
from rdflib import Graph
from rdflib.namespace import RDF, SH

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
ENCODING = os.getenv('ENCODING', 'utf-8')

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
