from typing import Optional

import requests
import json
import logging

logger = logging.getLogger(__name__)

def format_uri(term_label: str) -> str:
    return f'https://api.linkeddata.cultureelerfgoed.nl/queries/thesauri/Query-2/5/run?zoektermlabel={term_label.replace(' ', '+')}'

def get_term_uri_from_cht(term_label: str) -> Optional[str]:
    try:
        headers = {'accept': 'application/json'}
        response = requests.get(format_uri(term_label), headers=headers, timeout=100)
        items = json.loads(response.content, object_hook=(dict[str, str]))
        for item in items:
            if item['concept'] and item['prefLabel'] == term_label.lower():
                return item['concept']
    except KeyError as ke:
        logger.info('Did not find cht term: %s', str(ke))

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    logger.info(get_term_uri_from_cht('Erfgoed'))

if __name__ == '__main__':
    main()