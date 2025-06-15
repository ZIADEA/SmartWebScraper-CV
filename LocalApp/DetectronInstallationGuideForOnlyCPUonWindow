# guide_installation_detectron2_windows

Ma méthode pour installer detectron2 sous Windows 10 avec Anaconda (9 avril 2022)

Voici le fichier d'environnement qui comprend 2 types de pytorch : celui avec GPU (compatible CUDA) et celui avec CPU uniquement.

La première chose à faire est de cloner le [dépôt detectron2](https://github.com/facebookresearch/detectron2) :

    git clone https://github.com/facebookresearch/detectron2.git

Et les prérequis pour Windows 10 :

1. Ninja pour Windows (Pour référence, voir le [site web Ninja Build](https://ninja-build.org/))
2. Installer [MinGW 64-bit](https://sourceforge.net/projects/mingw/) (CygWin fonctionne aussi)
3. Installer Visual Studio Community 2019
4. Installer Nvidia CUDA 11.0 (Ou vérifier la version recommandée dans le [guide](https://pytorch.org/))

Les prérequis pour votre environnement Python avec anaconda :

1. Python 3.8 
2. Installer pytorch pour cuda >=11.0 (pour référence voir le [site web Pytorch](https://pytorch.org/)). Exemple :
   
       conda install pytorch torchvision torchaudio cudatoolkit=11.0 -c pytorch
  
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

Pour installer detectron2, voir [ici](https://github.com/facebookresearch/detectron2)

## Optionnel

Au lieu d'installer manuellement l'environnement anaconda pour installer detectron2, voici le fichier d'environnement anaconda (.yaml) que vous pouvez utiliser.

Après avoir importé l'environnement virtuel, la prochaine étape consiste à configurer detectron2 :

* Définir les distutils
  
      SET DISTUTILS_USE_SDK=1
    
* Appeler le fichier **vcvars64.bat** dans votre fenêtre cmd :
  
      call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
      
* Aller dans le dossier detectron2 et insérer cette commande :
  
      python setup.py build develop
   
* Ensuite, vous pouvez vérifier l'installation en testant pytorch et detectron2 (Voir le guide officiel [ici1](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) 
ou [ici2](https://detectron2.readthedocs.io/en/latest/tutorials/getting_started.html) pour confirmer l'installation).

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
