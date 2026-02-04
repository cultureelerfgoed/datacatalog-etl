import requests
import json
import os
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, DCAT, RDF

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
mapping = {}

def main():
    url = "https://kennis.cultureelerfgoed.nl/api.php"

    get_params = {
        'action': "ask",
        'query': '[[Categorie:Datasets]]|limit=500|?Status|?Batch|?Naam|?Dataset type|?Omschrijving|?Zichtbaar in Erfgoedatlas|?Dataset|?Bronurl|?Dataset creatie|?Dataset domein|?Dataset rubriek|?Dataset beperkingen',
        'format': 'json'
    }
    response = requests.get(url, params=get_params, timeout=100)
    datacatalog_json = json.loads(response.text)

    #with open('datacatalog.json') as f:
    #    datacatalog_json = json.load(f)
    
    if datacatalog_json:
        graph = Graph(identifier=GRAPH_ID)
        for result in datacatalog_json['query']['results']:
            dataset_node = URIRef(datacatalog_json['query']['results'][result]['fullurl'])
            dataset_properties = datacatalog_json['query']['results'][result]['printouts']
            print(str(dataset_properties))
            graph.add((dataset_node, RDF.type, DCAT.dataset))
            graph.add((dataset_node, DCTERMS.title, Literal(dataset_properties['Naam'])))
            graph.add((dataset_node, DCTERMS.description, Literal(dataset_properties['Omschrijving'])))
            graph.add((dataset_node, DCAT.mediaType, Literal(dataset_properties['Dataset type'])))
            
    else:
        print("Received empty response.")

if __name__ == '__main__':
    main()