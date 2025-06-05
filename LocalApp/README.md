## TOUT CE QUI EST REQUI POUR TESTER L APPLICATION EN LOCAL SUR VOTRE ORDINATEUR PERSONNEL : 


## Navigation dans l interface : 
page 1 : 
bienvenu dans votre scrapper inteligent 

se connecter : 
	option : utilisateur --> page 1.1
		 administrateur --> page 1.2

page 1.2 :
authentification :
	mail : djeryala@gmail.com
	mot de passe : DJERI
si incorrect --> page 1.2
si correct page --> 1.2.1

page 1.2.1 : 
tableau de bord : 
	voir les lien des site qui on été passer --> page 1.2.1.1
	voir les images annoter des prediction valider par human feed back de l utilisateur et sauvegarder en format coco dans le dossier (human data )  --> page 1.2.1.2
	voir les images annoter par l utilisateur lui meme et valider par lui et sauvegarder en format coco dans le dossier (human data )  --> page 1.2.1.3
	vor combien d image avons nous dans le dossier (fine tune data )-->page 1.2.1.4


page 1.2.1.1 : 
liens des sites qui on été passer dans l application

page 1.2.1.2 : 
images annoter des prediction valider afficher en grille 
chliquer si image nou renvoi ver --> page 1.2.1.2.1

page 1.2.1.2.1: 
affiche l image sur laquelle on vien de cliquer +
option : 
	valider l image alors l image et les fichier json de predicion son envoyer vers (fine tune data ) et est supprimer dans human data
 format coco
	supprimer l image du le dossier (human data )
	modifier l annotation page A.

page 1.2.1.3 : 
images annoter par l utilisateur valider afficher en grille 
cliquer si image nous renvoi ver --> page 1.2.1.3.1

page 1.2.1.3.1 : 
affiche l image sur laquelle on vien de cliquer +
option : 
	valider l image alors l image et les fichier json de predicion son envoyer vers (fine tune data )
 format coco
	supprimer l image du le dossier (human data )
	modifier l annotation page 1. 	

page A. 
annotation des image dans notre interface avec iframe de roboflow

page 1.2.1.4 : 
	affiche nombre d image présente dans le data coco (fine tune data )

	option : lancer le fintunning .
NB (apres les fine tunning les image du fine tune data sont supprimer )


page 1.1 : 

l utilisateur entre son lien et envoie (la capture est faite par playwright)--> page 1.1.2

page 1.1.2 :
affiche l image capture + 
option : 
	poser une question --> page 1.1.2.1
	sauvegarder l image --> page 1.1.2.2

page 1.1.2.1 :
afficher : "vous préférez que qui vous réponde ?"
CHAT GPT -->

 NLP classic >

page 1.1.2.1.1 :
l'utilisateur saisit sa question qui est envoyée à l'API ChatGPT.
La réponse générée s'affiche en bas de page.


page 1.1.2.1.2 :
l'utilisateur pose sa question.
Le texte de la page est extrait avec PaddleOCR puis traité localement avec les sentence transformers pour fournir une réponse affichée en bas.

page 1.1.2.2 : 
approter des modification ?
option : 
	oui --> page 1.1.2.2.1
	non -->	page Tn.
	
page Tn. : 
montrer la capture du site + bouton pour telecharger l image  



page 1.1.2.2.1 : 
on affiche l image annoter par le model  (toute les boxe detecter pae le model sur l image )+ 
options des box a supprimer  : 
	depend des classe detecter par le model 
bouton valider les choix --> page To

feed back
 le model a t il  bien detecter les boxe presente sur votre capture ?
option : 
	oui (l image et les prediction von dans le data human data en format coco) -->page To.
	non -->page FA.


page FA. :
 pouver vous nous vous meme annoter l image 
oui --> page B. 

page B. :
annotation des image dans notre interface avec iframe de roboflow
boutton valider --> page B1.

page B1. : 
supprimer des boxe de votre image ?
oui --> page B1.1
non -->page Tou.

page B1.1 :
on affiche l image annoter par le utilisateur  (toute les boxe detecter pae le model sur l image )+ 
options des box a supprimer  : 
	depend des classe detecter par le model 
bouton valider les choix --> page To




page To. : 
montrer la capture du site annoter par le model + bouton pour telecharger l image editer ou on a remove les zone choisi par l utilisateur .

page Tou. : 
montrer la capture du site annoter par l utilisateur + bouton pour telecharger l image 






