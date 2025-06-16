# Makefile pour SmartWebScraper-CV Documentation

# Variables
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = docs/source
BUILDDIR     = docs/build

# Aide par défaut
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Nettoyage
clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Documentation nettoyée."

# Construction HTML
html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Build HTML terminé. Les fichiers sont dans $(BUILDDIR)/html/"

# Construction PDF
latexpdf:
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Build PDF terminé. Le fichier est dans $(BUILDDIR)/latex/"

# Serveur de développement
serve:
	@echo "Démarrage du serveur de développement..."
	@cd $(BUILDDIR)/html && python -m http.server 8000

# Installation des dépendances
install:
	@echo "Installation des dépendances..."
	@pip install -r docs/requirements.txt

# Construction complète
all: clean install html
	@echo "Documentation construite avec succès!"

# Vérification des liens
linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Mode surveillance (autoreload)
watch:
	@echo "Mode surveillance activé. Ctrl+C pour arrêter."
	@sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Déploiement ReadTheDocs (simulation locale)
rtd-build:
	@echo "Simulation build ReadTheDocs..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" -D language=fr $(SPHINXOPTS) $(O)
	@$(SPHINXBUILD) -b epub "$(SOURCEDIR)" "$(BUILDDIR)/epub" -D language=fr $(SPHINXOPTS) $(O)

.PHONY: help clean html latexpdf serve install all linkcheck watch rtd-build
