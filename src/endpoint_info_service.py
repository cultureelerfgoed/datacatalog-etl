import json
import os
import logging
import requests
from rdflib import Graph, Node
from rdflib.namespace import RDF, SH
from urllib.parse import urlsplit


OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
BASE_URI = 'https://linkeddata.cultureelerfgoed.nl/'
QUERY_ENDPOINT = 'https://api.linkeddata.cultureelerfgoed.nl/queries/'
ACCOUNTS = {'rce', 'thesauri'}

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def get_dataset_uri(accountname='', datasetname=''):
    if datasetname != '' and accountname != '':
        return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/{datasetname}/'
    elif accountname != '':
        return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/'
    else:
        return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/'


def get_service_uri(datasetname: str, accountname:str):
    return f'https://api.{urlsplit(BASE_URI).hostname}/datasets/{accountname}/{datasetname}/services/'

def get_query_uri(accountname=None):
    if accountname:
        return f'https://api.{urlsplit(BASE_URI).hostname}/queries/{accountname}/'
    else:
        return f'https://api.{urlsplit(BASE_URI).hostname}/queries/'

def get_data(q_url: str) -> dict:
    """ Validate against endpoint """
    headers = {'accept': 'text/plain'}
    response = requests.get(q_url, headers=headers, timeout=100)
    r_obj = json.loads(response.content)
    logger.info('Got %i items from %s.', len(r_obj), q_url)
    ds = dict()

    for item in r_obj:
        # for each dataset call service description endpoint if the serviceCount is not 0
        if item.get('serviceCount') != 0:
            a_nm = item.get('owner')['accountName']
            s_uri = get_service_uri(item.get('name'), a_nm)
            s_response = requests.get(s_uri, headers=headers, timeout=100)
            s_obj = json.loads(s_response.text)
            
            ds[item.get('name')] = {'endpoint': s_obj[0].get('endpoint'), 
                                    'description': item.get('description'), 
                                    'displayName': item.get('displayName'), 
                                    'createdAt': item.get('createdAt')}
    return ds

def get_services():
    s_dict = get_data(get_dataset_uri())
    for account in ACCOUNTS:
        s_dict = s_dict | get_data(get_dataset_uri(account))
    logger.info('Retrieved %i sparql endpoints.', len(s_dict))
    return s_dict

def main():
    """ main runner for workflow """
    for key, service in get_services().items():
        logger.info('%s: %s', key, service['endpoint'])
    
if __name__ == '__main__':
    main()