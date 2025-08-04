# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SPARC FUSE'
copyright = '2025, Haberbusch, M et al.'
author = 'Haberbusch et al.'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",           # Für NumPy- und Google-Style-Docstrings
    "sphinx_autodoc_typehints",      # Für Typannotationen
    "myst_parser",                   # Für Markdown-Unterstützung (optional)
    "sphinx_markdown_builder"
]

templates_path = ['_templates']
exclude_patterns = []


import os
import sys

# Pfad hinzufügen
path = os.path.abspath('../..')
sys.path.insert(0, path)

# Zur Überprüfung ausgeben
print(f"Hinzugefügter Pfad: {path}")
print(f"sys.path enthält jetzt: {sys.path}")

# Teste, ob dein Modul importiert werden kann
try:
    import mein_modul
    print(f"Modul erfolgreich importiert: {mein_modul.__file__}")
except ImportError as e:
    print(f"Fehler beim Import: {e}")

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',        # Automatische Dokumentation aus Docstrings
    'sphinx.ext.napoleon',       # Google/NumPy Docstring-Support
    'sphinx.ext.viewcode',       # Links zum Quellcode
    'sphinx.ext.intersphinx',    # Verlinkung zu anderen Sphinx-Dokumentationen
    'sphinx_rtd_theme',          # Read the Docs Theme
    'sphinx.ext.autodoc.typehints',  # Typehints in der Dokumentation
]

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'   # Alternatives: 'alabaster', 'sphinx_material', 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Napoleon settings for docstrings ----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Intersphinx mapping ----------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    # Weitere externe Dokumentationen hinzufügen
}
