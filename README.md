# Comparaison pluie - aérosols désertiques

 
IRD Cayenne
ENSG Géomatique

## Contexte

Ce code a été mis en place par Baptiste Rivière, étudiant en 2e année de formation Ingénieur à l'ENSG Géomatique dans le cadre d'un stage au sein de l'IRD de Cayenne.

Il s'agit d'une application permettant de mettre en évidence la relation pluie - PM10 à partir de données au sol et d'images satellites en Guyane.

Les différents dossiers sont présentés ci-dessous, les scripts sont rédgigés dans le langage de programmation python.

La version mise à jour de ce code est accessible publiquement sur le lien github suivant
https://github.com/baptisteRiviere/IRD_pluie_aerosols


## contenu

### downloading

Il s'agit du dossier contenant des codes permettant le téléchargement de différentes données satellites. un fichier README spécifique y est présent pour la mise en place des clés permettant le téléchargement.

### Images

Ce dossier contient des fichiers associés à différentes classes, celles-ci fournissent les outils permettant d'appeler simplement tout type de fichier image, de l'extraire et de la projeter.
Un diagramme de classe est disponible dans ce dossier.

### pluie

Le dossier pluie permet de mesurer la qualité des estimations IMERG, de télécharger certaines images MO et IR et de les comparer avec la pluviométrie (*main_pluie.ipynb*).
Le script *ground_truth_rain.py* permet de manipuler les données acquises par les pluviomètres de Méétéo France en Guyane.

### rain_PM10_relation

le script *signal_analyse* présent dans ce dossier permet d'associer deux séries temporelles de mesures. Il met alors en place des outils statistiques de mesure telle que la fonction de cohérence ou le convergent cross mapping.

### tools

Il s'agit de quelques fonctions utiles dans différents dossiers.

## Environnement

Ce code a été conçu sous python 3.9.13, les packages demandés sont répértoriés dans le fichier requirements.txt. 

Les librairies principales sont listées ci-dessous

- Cartopy (affichage géoréférencé sous matplotlib)
- GDAL (gestion des données raster)
- json (gestion des fichiers json)
- matplotlib (affichage des images et des figures)
- netCDF4 (gestion des fichiers netcdf)
- numpy (calculs sur les matrices)
- pandas (gestion des tableaux de données)
- pyresample (rééchantillonage image)
- satpy (permet de manipuler les images IR de eumetsat)
- sentinelsat (API permettant le téléchargement des images Sentinel)
- skccm (fonction de convergent cross mapping)













