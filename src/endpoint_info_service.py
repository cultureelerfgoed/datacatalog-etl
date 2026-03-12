import json
import os
import logging
import requests
from urllib.parse import urlsplit

ENCODING = os.getenv('ENCODING', 'utf-8')
BASE_URI = os.getenv('BASE_URI', 'https://linkeddata.cultureelerfgoed.nl/')
ACCOUNTS = {'rce', 'thesauri'}

logger = logging.getLogger(__name__)

def get_dataset_uri(accountname='', datasetname=''):
    if datasetname != '' and accountname != '':
        return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/{datasetname}/'
    elif accountname != '':
        return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/'
    else:
        return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/?limit=200'

def get_speedy_uri(accountname:str, datasetname: str):
    return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/{datasetname}/sparql'

def get_service_uri(accountname:str, datasetname: str):
    return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/{datasetname}/services/'

def get_data(q_url: str) -> dict:
    """ Validate against endpoint """
    headers = {'accept': 'text/plain'}
    response = requests.get(q_url, headers=headers, timeout=100)
    r_obj = json.loads(response.content)
    logger.info('Got %i items from %s.', len(r_obj), q_url)
    ds = dict()

    for item in r_obj:
        # for each dataset call service description endpoint if the serviceCount is not 0
        a_nm = item.get('owner')['accountName']
        ds[item.get('name')] = {'endpoint': get_speedy_uri(a_nm, item.get('name')), 
                                'description': item.get('description'), 
                                'displayName': item.get('displayName'), 
                                'createdAt': item.get('createdAt'),
                                'updatedAt': item.get('updatedAt')}
    return ds

def get_services():
    """ Returns all speedy endpoints  """
    s_dict = get_data(get_dataset_uri())
    logger.info('Retrieved %i sparql endpoints.', len(s_dict))
    return s_dict

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    for key, service in get_services().items():
        logger.info('%s: %s', key, service['endpoint'])
    
if __name__ == '__main__':
    main()