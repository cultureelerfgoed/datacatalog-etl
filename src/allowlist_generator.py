import os
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO
import endpoint_info_service 

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
ALLOWLIST_PATH = os.getenv('ALLOWLIST_PATH', 'allowlist.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
ALLOWLIST = {'https://kennis.cultureelerfgoed.nl/index.php/Dataset/45': 'cht',
             'https://kennis.cultureelerfgoed.nl/index.php/Dataset/5': 'archeologischbasisregister',
             'https://kennis.cultureelerfgoed.nl/index.php/Dataset/105': 'Rijksmonumenten-sdo',
             'https://kennis.cultureelerfgoed.nl/index.php/Dataset/102': 'groenaanleg'}
             # cho

# --- Make allowlist graph  ---
def generate_allowlist() -> Graph:
    graph = Graph()
    services = endpoint_info_service.get_services()
    for key, value in ALLOWLIST.items():
        graph.add((URIRef(key), RDF.type, SDO.DataDownload))
        d_item = services.get(value)
        graph.add((URIRef(key), SDO.identifier, Literal(value)))
        if d_item:
            if 'endpoint' in d_item:
                graph.add((URIRef(key), SDO.contentUrl, URIRef(d_item['endpoint'])))        
            if 'displayName' in d_item:
                graph.add((URIRef(key), SDO.name, Literal(d_item['displayName'])))
            if 'description' in d_item:
                graph.add((URIRef(key), SDO.description, Literal(d_item['description'])))
            if 'createdAt' in d_item:
                graph.add((URIRef(key), SDO.dateCreated, Literal(d_item['createdAt'])))
            if 'updatedAt' in d_item:
                graph.add((URIRef(key), SDO.dateModified, Literal(d_item['updatedAt'])))
            
    return graph

def main():
    graph = generate_allowlist()
    graph.serialize(format=OUTPUT_FILE_FORMAT, destination=ALLOWLIST_PATH, encoding=ENCODING, auto_compact=True)    

if __name__ == '__main__':
    main()
