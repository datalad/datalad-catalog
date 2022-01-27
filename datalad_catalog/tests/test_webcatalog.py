
from ..catalog import Catalog
from ..webcatalog import WebCatalog
import pytest
from datalad.support.exceptions import InsufficientArgumentsError



@pytest.fixture
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    return WebCatalog(location=catalog_path)


