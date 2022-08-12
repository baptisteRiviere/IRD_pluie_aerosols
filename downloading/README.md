
# Téléchargement images satellites

Ce dossier contient les scripts permettant de télécharger les images satellites listées ci-dessous. Des exemples de clés associées sont présentées dans le dossier "keys" de "data".

## IMERG

Les estimations de pluie IMERG sont disponibles à partir des scripts dans le dossier API_IMERG.
Leur téléchargements demande la création d'un compte à l'URL urs.earthdata.nasa.gov
Un fichier nommé ".netrc" doit être créé à la racine du dossier user, ce fichier doit contenir la ligne suivante :
- machine urs.earthdata.nasa.gov login <login> password <password>

## NSIDC

Les images micro ondes du capteur SSMIS de la NSIDC sont accessibles à partir de l'API correspondante.
La clé d'accès doit être crée à l'URL https://nsidc.org/data/NSIDC-0630/versions/1
elle doit être donnée dans un fichier comme présenté ci-dessous, il est conseillé de modifier le fichier mdp_NSIDC.json dans le dossier keys de data.

- {"username": "<username>","password": "<password>}

## Meteosat

Les images infrarouge du capteur SEVIRI de Meteosat sont accessibles à partir de l'API correspondante.
La clé d'accès doit être crée à l'URL https://data.eumetsat.int/data/map/EO:EUM:DAT:MSG:HRSEVIRI#
elle doit être donnée dans un fichier, il est conseillé de modifier le fichier eds.key dans le dossier keys de data. 
Le fichier doit contenir une clé et un identifiant généré à partir de la plateforme sur internet.

## VIIRS

Le téléchargement des images AOT de VIIRS ne demande pas de création de compte

## Sentinel-5P

Le téléchargement des images de l'aerosol index de sentinel-5P ne demandent pas de création de compte.


