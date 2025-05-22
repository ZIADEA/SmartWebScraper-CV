Modèle de détection
===================

Le modèle utilisé est basé sur **Fast_RCNN de Detectron2**, fine-tuné sur un dataset personnalisé au format COCO.

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

- **mAP (IoU = 0.5)** : 81%
- **IoU moyen** : 0.73

Le modèle est en amélioration continue grâce à l'intégration de nouvelles données annotées via feedback utilisateur.

Modèle de d extraction de texte
===================
Le modèle utilisé est le model preentrainé  **PaddleOCR **
pour l’extraction de texte.
Il est capable de détecter et d'extraire du texte à partir d'images, y compris des textes en plusieurs langues.

Modèle utilisé pour la reponse aux questions 
===================
Le modèle (en cours de développement) est basé sur **--** et **--** pour la gestion des questions-réponses.