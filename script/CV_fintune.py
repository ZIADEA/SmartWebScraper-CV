import os
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data.datasets import register_coco_instances
from detectron2.engine.defaults import DefaultTrainer
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader

# Configuration
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_DC5_3x.yaml"))

# Définition des datasets (⚠️ attention aux slashs inversés sur Windows)
cfg.DATASETS.TRAIN = ("web_scrapper_images_annotes.v2i.coco/train",)
cfg.DATASETS.TEST = ("web_scrapper_images_annotes.v2i.coco/valid",)

# Chargement des poids et paramètres d'entraînement
cfg.DATALOADER.NUM_WORKERS = 2
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_DC5_3x.yaml")
cfg.SOLVER.IMS_PER_BATCH = 2
cfg.SOLVER.BASE_LR = 0.00025
cfg.SOLVER.MAX_ITER = 1000
cfg.SOLVER.STEPS = []
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 64
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 18  # nombre total de classes
cfg.OUTPUT_DIR = "./output_detectron_web"
cfg.MODEL.DEVICE = "cpu"

# Création des dossiers nécessaires
os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

# Enregistrement des datasets personnalisés
register_coco_instances(
    "web_scrapper_images_annotes.v2i.coco/train", {},
    "web_scrapper_images_annotes.v2i.coco/train/_annotations.coco.json",
    "web_scrapper_images_annotes.v2i.coco/train"
)
register_coco_instances(
    "web_scrapper_images_annotes.v2i.coco/valid", {},
    "web_scrapper_images_annotes.v2i.coco/valid/_annotations.coco.json",
    "web_scrapper_images_annotes.v2i.coco/valid"
)
register_coco_instances(
    "web_scrapper_images_annotes.v2i.coco/test", {},
    "web_scrapper_images_annotes.v2i.coco/test/_annotations.coco.json",
    "web_scrapper_images_annotes.v2i.coco/test"
)

# Entraînement
trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()

# Évaluation sur le jeu de test
evaluator = COCOEvaluator("web_scrapper_images_annotes.v2i.coco/test", cfg, False, output_dir=cfg.OUTPUT_DIR)
test_loader = build_detection_test_loader(cfg, "web_scrapper_images_annotes.v2i.coco/test")

print("🧪 Évaluation en cours...")
inference_on_dataset(trainer.model, test_loader, evaluator)
