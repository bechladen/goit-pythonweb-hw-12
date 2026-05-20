import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Required env vars for importing app modules during autodoc.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "docs-secret")

project = "Contacts API"
author = "Student"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "nature"
