Modèle de détection
===================

Le modèle utilisé est basé sur **Detectron2**, fine-tuné sur un dataset personnalisé au format COCO.

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
- Les annotations sont générées automatiquement via le modèle, et peuvent être corrigées manuellement par les utilisateurs via l interface utilisateru de notr application (actuellement en developpement ).

Performance 
---------------------

- **mAP (IoU = 0.5)** : 81%
- **IoU moyen** : 0.73

Le modèle est en amélioration continue grâce à l'intégration de nouvelles données annotées via feedback utilisateur.
