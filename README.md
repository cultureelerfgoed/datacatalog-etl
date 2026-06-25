# ETL voor het publiceren van RCE datasets op het NDE Datasetregister

```mermaid
flowchart LR;
    Proza(Proza) --> KB(Kennisbank) --> ETL(ETL) --> LDV(Linked Data Voorziening) --> NDE(NDE Datasetregister)
```

Deze ETL voert de volgende stappen uit:
1. Haalt de lijst van datasets op die gepubliceerd zijn op de Kennisbank van de Rijksdienst voor Cultureel Erfgoed.
2. Haalt de lijst van gepubliceerde endpoints op van de Linked Data Voorziening van de RCE.
3. Transformeert de metadata over de datasets naar schema.org volgens de richtlijn van het NDE Datasetregister, en filtert de datasets die hier niet aan voldoen er uit.
4. Valideert de transformatie via de validatie API van het Netwerk Digitaal Erfgoed.
5. Publiceert de set van datasets op [linkeddata.cultureelerfgoed.nl](https://linkeddata.cultureelerfgoed.nl/rce/datacatalog-rce/).
6. De data wordt opgehaald en opgenomen in het NDE Datasetregister. 

## Sequentiediagram ETL
```mermaid
sequenceDiagram;
    actor beheerder
    participant Proza 
    participant Kennisbank
    participant ETL
    participant Linked Data Voorziening
    participant Netwerk Digitaal Erfgoed
    
    beheerder->>Proza:ophalen intern datasetregister
    Proza-->>beheerder:
    beheerder->>Kennisbank:publicatie intern datasetregister
    loop RCE Datacatalog ETL
        ETL->>Linked Data Voorziening:ophalen beschikbare endpoints
        Linked Data Voorziening-->>ETL:
        ETL->>Kennisbank:ophalen intern datasetregister
        Kennisbank-->>ETL:
        ETL->>ETL:transformatie naar linked data
        ETL->>Netwerk Digitaal Erfgoed:validatie op body
        Netwerk Digitaal Erfgoed-->>ETL:
        ETL->>Linked Data Voorziening:publicatie van datasets waarvoor endpoints bestaan
        ETL->>Linked Data Voorziening:sync
        ETL->>Netwerk Digitaal Erfgoed:validatie op endpoint
        Netwerk Digitaal Erfgoed->>Linked Data Voorziening:
        Linked Data Voorziening-->>Netwerk Digitaal Erfgoed:
        Netwerk Digitaal Erfgoed-->>ETL:
    end
    Netwerk Digitaal Erfgoed->>Linked Data Voorziening:opname in NDE datasetregister
    Linked Data Voorziening-->>Netwerk Digitaal Erfgoed:
```

## Datamodel

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}} }%%
flowchart TD
classDef Literal fill:#ffffff,stroke:#000000,color:;
classDef Literal_URI fill:#ffffff,stroke:#000000,color:;
classDef Multi fill:#cccccc,stroke:#000000,color:;
classDef Multi_URI fill:#cccccc,stroke:#000000,color:;
0(["schema:Dataset"]) -->|schema:publisher| 1(["schema:Organization"])
1(["schema:Organization"]) -->|schema:sameAs| 2["xsd:anyURI"]:::Literal
0(["schema:Dataset"]) -->|schema:datePublished| 3["xsd:string"]:::Literal
1(["schema:Organization"]) -->|schema:alternateName| 4["xsd:string"]:::Literal
1(["schema:Organization"]) -->|schema:name| 5["xsd:string"]:::Literal
0(["schema:Dataset"]) -->|schema:description| 6["xsd:string"]:::Literal
0(["schema:Dataset"]) -->|schema:name| 7["xsd:string"]:::Literal
0(["schema:Dataset"]) -->|schema:dateCreated| 8["xsd:string"]:::Literal
0(["schema:Dataset"]) -->|schema:keywords| 9["xsd:string"]:::Literal
10(["schema:DataDownload"]) -->|schema:usageInfo| 11["xsd:anyURI"]:::Literal
1(["schema:Organization"]) -->|schema:contactPoint| 12(["schema:ContactPoint"])
0(["schema:Dataset"]) -->|schema:distribution| 10(["schema:DataDownload"])
0(["schema:Dataset"]) -->|schema:dateModified| 13["xsd:string"]:::Literal
12(["schema:ContactPoint"]) -->|schema:email| 14["xsd:string"]:::Literal
10(["schema:DataDownload"]) -->|schema:description| 15["xsd:string"]:::Literal
1(["schema:Organization"]) -->|schema:identifier| 16["xsd:string"]:::Literal
10(["schema:DataDownload"]) -->|schema:contentUrl| 17["xsd:anyURI"]:::Literal
10(["schema:DataDownload"]) -->|schema:dateCreated| 18["xsd:string"]:::Literal
0(["schema:Dataset"]) -->|schema:about| 19["xsd:anyURI"]:::Literal
0(["schema:Dataset"]) -->|schema:license| 20["xsd:anyURI"]:::Literal
10(["schema:DataDownload"]) -->|schema:dateModified| 21["xsd:string"]:::Literal
0(["schema:Dataset"]) -->|schema:creator| 1(["schema:Organization"])
0(["schema:Dataset"]) -->|schema:inLanguage| 22["xsd:string"]:::Literal
12(["schema:ContactPoint"]) -->|schema:name| 23["xsd:string"]:::Literal
```

## Installatie

```
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Uitvoeren

```
python src/generate_allowlist.py
python src/datacatalog_service.py
python src/validator.py --path 'artifact-data.jsonld' --method 'GET' --status 200
```
## Configureren

De configuratiewaardes van de workflow kunnen aangepast worden in het bestand config/config.yml. Zie config/config.yml voor uitgebreidere documentatie over de mogelijkheden. Verdere configuratie staat in de workflow bestanden in .github/workflows/.
