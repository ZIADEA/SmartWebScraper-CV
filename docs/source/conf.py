# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SmartWebScraper-CV'
copyright = '2025, DJERI-ALASSANI OUBENOUPOU'
author = 'DJERI-ALASSANI OUBENOUPOU'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/ZIADEA/SmartWebScraper-CV",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": False,
    "show_navbar_depth": 2,
    "path_to_docs": "docs/source",
}

html_title = "SmartWebScraper-CV"


