import os
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
WHITELIST_PATH = os.getenv('TARGET_FILEPATH', 'datacatalog-whitelist.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')

# --- Make whitelist graph  ---
def generate_whitelist() -> Graph:
    graph = Graph(identifier='https://linkeddata.cultureelerfgoed.nl/datacatalog-whitelist')
    # datacatalog definition
    graph.add((URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/45'), RDF.type, SDO.DataDownload))
    graph.add((URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/45'), SDO.contentUrl, Literal('https://api.linkeddata.cultureelerfgoed.nl/datasets/thesauri/cht/services/cht-jena/sparql')))
    graph.add((URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/5'), RDF.type, SDO.DataDownload))
    graph.add((URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/5'), SDO.contentUrl, Literal('https://api.linkeddata.cultureelerfgoed.nl/datasets/thesauri/archeologischbasisregister/services/archeologischbasisregister-jena/sparql')))
    graph.add((URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/147'), RDF.type, SDO.DataDownload))
    graph.add((URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/147'), SDO.contentUrl, Literal('https://api.linkeddata.cultureelerfgoed.nl/datasets/thesauri/referentienetwerk/sparql')))    
    return graph

def main():
    graph = generate_whitelist()
    graph.serialize(format=OUTPUT_FILE_FORMAT, destination=WHITELIST_PATH, encoding=ENCODING, auto_compact=True)    

if __name__ == '__main__':
    main()