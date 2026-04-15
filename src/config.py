
import os
from rdflib.namespace import SDO

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'datacatalog.jsonld')
SRC_URI = os.getenv('SRC_URI', 'https://kennis.cultureelerfgoed.nl/api.php')
ENCODING = os.getenv('ENCODING', 'utf-8')
BASE_URI = os.getenv('BASE_URI', 'https://linkeddata.cultureelerfgoed.nl')
VALIDATION_API = os.getenv('VALIDATION_API', 'https://datasetregister.netwerkdigitaalerfgoed.nl/api/datasets/validate')

KENNISBANK_ENDPOINT = 'Sparql-endpoint'
KENNISBANK_BEPERKINGEN = 'Dataset beperkingen'
KENNISBANK_NAAM = 'Naam'
KENNISBANK_OMSCHRIJVING = 'Omschrijving'
KENNISBANK_RUBRIEK = 'Dataset rubriek'
KENNISBANK_DOMEIN = 'Dataset domein'

KB_DC_QUERY = '[[Categorie:Datasets]]|limit=500|?Status|?Batch|?Naam|?Dataset type|?Omschrijving' \
'|?Zichtbaar in Erfgoedatlas|?Dataset|?Bronurl|?Dataset creatie|?Dataset domein|?Dataset rubriek|?Dataset beperkingen|?Sparql-endpoint'

ORG_URI = 'https://www.cultureelerfgoed.nl'
ORG_NAME = 'Rijksdienst voor het Cultureel Erfgoed'
ORG_SAME_AS = 'https://standaarden.overheid.nl/owms/terms/Rijksdienst_voor_het_Cultureel_Erfgoed'
ORG_CONTACT_NAME = 'Infodesk van de RCE'
ORG_CONTACT_EMAIL = 'thesauri@cultureelerfgoed.nl'
ORG_ISIL = 'NL-AmfRCE'
ORG_ALTNAME = 'Cultural Heritage Agency of the Netherlands'

KENNISBANK_MAPPING = {
    KENNISBANK_NAAM: SDO.name,
    KENNISBANK_OMSCHRIJVING: SDO.description,
    KENNISBANK_RUBRIEK: SDO.genre,
}

LICENSES = {'CC BY-SA v4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
            'CC BY': 'https://creativecommons.org/licenses/by/4.0/',
            'CC0 1.0': 'https://creativecommons.org/publicdomain/zero/1.0/',
            'default': 'https://creativecommons.org/licenses/by/4.0/'}