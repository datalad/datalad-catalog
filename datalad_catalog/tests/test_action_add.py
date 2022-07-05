from ..webcatalog import WebCatalog
from ..catalog import Catalog
import pytest
from datalad.support.exceptions import InsufficientArgumentsError

catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/vue_app.js",
    "assets/style.css",
    "artwork",
    "index.html",
]
