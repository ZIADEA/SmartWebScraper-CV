# guide_installation_detectron2_windows

Ma méthode pour installer detectron2 sous Windows 10 avec Anaconda (version CPU uniquement) (9 avril 2022)

Ce guide se concentre sur l'installation de detectron2 avec pytorch CPU uniquement.

La première chose à faire est de cloner le [dépôt detectron2](https://github.com/facebookresearch/detectron2) :

   git clone https://github.com/facebookresearch/detectron2.git


Les prérequis pour votre environnement Python avec anaconda :

1. Python 3.8 ou Python 3.10
2. Installer pytorch version CPU (pour référence voir le [site web Pytorch](https://pytorch.org/)). Exemple :
  
  Pour Python 3.8 :
  
      conda install pytorch torchvision torchaudio cpuonly -c pytorch
  
  Pour Python 3.10 :
  
      conda install pytorch torchvision torchaudio cpuonly -c pytorch
 
3. Installer Cython
  
      pip install cython
  
  ou
   
      conda install -c anaconda cython
   
4. Installer OpenCV
  
      pip install opencv-python

5. Installer Pywin32
  
      pip install pywin32
       
  ou
   
      conda install -c conda-forge pywin32

6. Installer pycocotools
  
      pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"

7. Installer git (si git n'est pas détecté dans votre cmd)
  
      conda install -c anaconda git
  
Pour les étapes, installez ces dépendances avant d'installer detectron2 dans votre environnement Python.

Enfin veiller vous placer dans le Dossier detectron2 cloner en local dans votre terminal 
puis assurer vous que il contient le fichier setup.py a sa racine 
puis executer : 
```Bash
conda install -e .
```

<div align="center">
  <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2FqMHJ5bnNyMmdtczR4MTIzbXVwYnhmYWIzajdya21pMmpqYnliMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT8qBepJQzUjXpeWU8/giphy.gif" alt="SmartWebScraper demonstration" width="500"/>
</div>


## Ajout

vous pouver vous documenter plus sur l instalation via : https://detectron2.readthedocs.io/en/latest/tutorials/getting_started.html#use-detectron2-apis-in-your-code

## Références :

**Detectron2**
@misc{wu2019detectron2,
 author =       {Yuxin Wu and Alexander Kirillov and Francisco Massa and
                 Wan-Yen Lo and Ross Girshick},
 title =        {Detectron2},
 howpublished = {\url{https://github.com/facebookresearch/detectron2}},
 year =         {2019}
}

**Pytorch**
https://pytorch.org/

**Forum Pytorch**
[Solution par le commentaire de RujunLong](https://discuss.pytorch.org/t/detectron-2-on-windows-10/93639/3)

**AugmentedStartups**
J'ai trouvé quelques solutions dans cette [vidéo](https://youtu.be/JC4D9kfZdDI) par AugmentedStartups

**Github Detectron2 Issue#9**
Vous pouvez voir d'autres solutions [ici](https://github.com/facebookresearch/detectron2/issues/9)
