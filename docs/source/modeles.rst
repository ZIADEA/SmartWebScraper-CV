Modèle de détection 
===================

Le modèle utilisé est basé sur **Fast_RCNN de Detectron2**, fine-tuné sur un dataset personnalisé au format COCO de **159 images**.

Classes détectées
-----------------

Voici la liste complète des classes détectées par notre modèle :

- advertisement
- chaine
- commentaire
- description
- footer
- header
- left sidebar
- likes
- logo
- media
- none access
- other
- pop up
- recommendations
- right sidebar
- suggestions
- title
- vues

> 💡 Ces classes ont été définies manuellement dans `MetadataCatalog.get("__unused").thing_classes`.

Format des annotations
----------------------

- Format COCO (fichier JSON)

Performance 
---------------------

- **AP (moyenne sur tous les IoU)** : 10.39%
- **AP50 (IoU = 0.5)** : 21.51%
- **AP75 (IoU = 0.75)** : 8.17%
- **APs (objets petits)** : 0.88%
- **APm (objets moyens)** : 16.92%
- **APl (objets larges)** : 18.32%

Performances par classe :
^^^^^^^^^^^^^^^^^^^^^^^^^

- **header** : 33.79%
- **footer** : 53.62%
- **advertisement** : 21.72%
- **pop up** : 26.05%
- **right sidebar** : 30.10%
- **media** : 12.43%
- **logo** : 2.82%
- **title** : 6.44%
- **chaine, commentaire, description, left sidebar, likes, none access, other, recommendations, suggestions, vues** : 0.00%

>Ces scores montrent que certaines classes sont bien détectées (footer, header...), tandis que d'autres nécessitent encore des données supplémentaires.

Le modèle est en **amélioration continue** grâce à l'intégration de nouvelles données annotées via feedback utilisateur.

Modèle de d'extraction de texte
===============================

Le modèle utilisé est le modèle pré-entraîné **PaddleOCR** pour l’extraction de texte.  
Il est capable de détecter et d'extraire du texte à partir d'images, y compris des textes en plusieurs langues.

Modèle utilisé pour la réponse aux questions 
============================================

Le modèle (en cours de développement) est basé sur **--** et **--** pour la gestion des questions-réponses.

