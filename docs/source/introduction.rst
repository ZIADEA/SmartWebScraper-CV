Introduction
============

Bienvenue dans la documentation officielle du projet **SmartWebScraper-CV**.

Ce projet a été développé dans le cadre d’un programme d’ingénierie en **Intelligence Artificielle et Technologie des Données** à l’ENSAM Meknès.  
Il vise à répondre à un défi croissant : **l'extraction d'information pertinente à partir de pages web complexes**, souvent protégées contre le scraping traditionnel.

Objectif du projet
------------------

Le but est de concevoir une application intelligente capable de :

- Capturer des pages web sous forme d'images (via Playwright ou Selenium)
- Détecter automatiquement les zones d’intérêt (header, pub, sidebar, contenu, etc.)
- Supprimer ou filtrer certaines parties selon les besoins
- Extraire les textes restants via OCR
- Permettre à l’utilisateur d’interroger dynamiquement le contenu via un model NLP

Pourquoi ce projet ?
--------------------

Les méthodes traditionnelles de scraping basées sur le HTML (comme BeautifulSoup, requests ou Selenium en mode texte) deviennent de plus en plus limitées face aux nouvelles pratiques de protection des contenus. Voici pourquoi une approche par **Computer Vision** s’impose :

- **Obfuscation du code HTML** : Le contenu réel est parfois masqué, encodé ou fragmenté volontairement pour empêcher son extraction directe.
- **JavaScript dynamique** : Les données sont souvent injectées après chargement via JavaScript, rendant le DOM difficile à intercepter sans exécuter entièrement la page.
- **Contenu sous forme d’image (PDF, PNG, SVG)** : Certains sites affichent les textes sous forme d’images (ou canvas) pour empêcher la copie ou la lecture automatique.
- **Interfaces riches et complexes** : Menus déroulants, carrousels, sliders et animations compliquent la lecture structurée du code HTML.
- **Pas d’API ou DOM volontairement inaccessible** : Les endpoints d’API sont inexistants, privés, ou nécessitent une authentification avancée.
- **Changements fréquents de structure** : Le scraping HTML est fragile face à la moindre modification de classe CSS ou de structure de balise.

Face à ces défis, la vision par ordinateur apporte une **approche agnostique et visuelle** : au lieu de lire le code, on lit **l’image rendue par le navigateur**, comme un humain.

L’IA permet alors :
- de **localiser visuellement** les zones d’intérêt (ex. : header, pub, contenu…),
- de **filtrer** ce qui n’est pas utile (pop-ups, sidebar…),
- d’**extraire le texte par OCR**,
- et même de **répondre à des questions sur le contenu** via NLP.

Ce projet démontre la faisabilité d’un scraping intelligent, **robuste, scalable et éthique**, basé sur une compréhension visuelle et linguistique des pages web.

À qui s’adresse cette documentation ?
-------------------------------------

Cette documentation s’adresse à plusieurs profils :

- Les **utilisateurs** souhaitant tester l’application
- Les **développeurs** souhaitant comprendre l’architecture du projet
- Les **étudiants** ou chercheurs intéressés par les approches alternatives de web scraping
- Les **recruteurs** ou enseignants souhaitant évaluer le niveau technique de l’équipe

Bonne lecture, et bienvenue dans l’univers de **SmartWebScraper-CV** !
