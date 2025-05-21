Modèle de détection
===================

Le modèle utilisé est basé sur **Detectron2**, fine-tuné sur un dataset personnalisé (format COCO).

Classes détectées
-----------------

- header
- footer
- ads
- sidebar
- title
- content
- media

Format des annotations
----------------------

- Format COCO (JSON)
- Générées automatiquement et manuellement selon le contexte

Performance (exemple)
---------------------

- mAP (IoU=0.5) : 81%
- IoU moyen : 0.73

Le modèle est en cours d’amélioration continue.
