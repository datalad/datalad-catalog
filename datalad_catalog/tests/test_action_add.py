import pytest
from datalad.support.exceptions import InsufficientArgumentsError

from datalad_catalog.catalog import Catalog
from datalad_catalog.webcatalog import WebCatalog

catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/vue_app.js",
    "assets/style.css",
    "artwork",
    "index.html",
]
