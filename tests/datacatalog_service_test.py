import json
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import datacatalog_service
from rdflib.namespace import SDO, RDF

def test_parse_json_to_graph_valid():
    desc = \
    '{' \
    '"query": {' \
    '    "results": {' \
    '        "Dataset/115": {' \
    '             "printouts": {' \
    '                 "Status": [],' \
    '                 "Batch": [],' \
    '                 "Naam": ["Tbl Diersoort (standaard) (BoneInfo)" ],' \
    '                 "Dataset type": [' \
    '                    "Gestructureerd-hierarchisch"' \
    '                 ],' \
    '                 "Omschrijving": [' \
    '                    "Deze dataset is een"' \
    '                 ],' \
    '                 "Zichtbaar in Erfgoedatlas": [' \
    '                    "Nee"' \
    '                 ],' \
    '                 "Dataset": [],' \
    '                 "Bronurl": [' \
    '                     "https://www.cultureelerfgoed.nl/onderwerpen/bronnen-en-kaarten/overzicht/"' \
    '                 ],' \
    '                 "Dataset creatie": [' \
    '                     "Inventarisatie"' \
    '                 ],' \
    '                 "Dataset domein": [' \
    '                     "Archeologie"' \
    '                 ],' \
    '                 "Dataset rubriek": [' \
    '                     "Archeologisch Erfgoed"' \
    '                 ],' \
    '                 "Dataset beperkingen": [' \
    '                     "Nee"' \
    '                 ],' \
    '                 "Sparql-endpoint": [ "https://test.cultureelerfgoed.nl/Dataset/115/sparql" ]' \
    '             },' \
    '             "fulltext": "Dataset/115",' \
    '             "fullurl": "https://kennis.cultureelerfgoed.nl/index.php/Dataset/115",' \
    '             "namespace": "0",' \
    '             "exists": "1",' \
    '             "displaytitle": "Tbl Diersoort (standaard) (BoneInfo)"' \
    '        }' \
    '    }' \
    '  }' \
    '}'

    graph = datacatalog_service.parse_json_to_graph(json.loads(desc))
    graph.print()
    assert len(list(graph.subjects(RDF.type, SDO.Dataset))) == 1
    assert len(list(graph.subjects(RDF.type, SDO.Organization))) == 1
    assert len(list(graph.subjects(RDF.type, SDO.DataDownload))) == 1
    assert len(list(graph.subjects(RDF.type, SDO.ContactPoint))) == 1

def test_parse_json_to_graph_no_endpoint():
    desc = \
    '{' \
    '"query": {' \
    '    "results": {' \
    '        "Dataset/115": {' \
    '             "printouts": {' \
    '                 "Status": [],' \
    '                 "Batch": [],' \
    '                 "Naam": ["Tbl Diersoort (standaard) (BoneInfo)" ],' \
    '                 "Dataset type": [' \
    '                    "Gestructureerd-hierarchisch"' \
    '                 ],' \
    '                 "Omschrijving": [' \
    '                    "Deze dataset is een"' \
    '                 ],' \
    '                 "Zichtbaar in Erfgoedatlas": [' \
    '                    "Nee"' \
    '                 ],' \
    '                 "Dataset": [],' \
    '                 "Bronurl": [' \
    '                     "https://www.cultureelerfgoed.nl/onderwerpen/bronnen-en-kaarten/overzicht/"' \
    '                 ],' \
    '                 "Dataset creatie": [' \
    '                     "Inventarisatie"' \
    '                 ],' \
    '                 "Dataset domein": [' \
    '                     "Archeologie"' \
    '                 ],' \
    '                 "Dataset rubriek": [' \
    '                     "Archeologisch Erfgoed"' \
    '                 ],' \
    '                 "Dataset beperkingen": [' \
    '                     "Nee"' \
    '                 ],' \
    '                 "Sparql-endpoint": []' \
    '             },' \
    '             "fulltext": "Dataset/115",' \
    '             "fullurl": "https://kennis.cultureelerfgoed.nl/index.php/Dataset/115",' \
    '             "namespace": "0",' \
    '             "exists": "1",' \
    '             "displaytitle": "Tbl Diersoort (standaard) (BoneInfo)"' \
    '        }' \
    '    }' \
    '  }' \
    '}'

    graph = datacatalog_service.parse_json_to_graph(json.loads(desc))
    graph.print()
    assert len(list(graph.subjects(RDF.type, SDO.Dataset))) == 0
    assert len(list(graph.subjects(RDF.type, SDO.Organization))) == 1
    assert len(list(graph.subjects(RDF.type, SDO.DataDownload))) == 0
    assert len(list(graph.subjects(RDF.type, SDO.ContactPoint))) == 1