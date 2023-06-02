

from pathlib import Path
import pytest
from datalad_catalog.webcatalog import WebCatalog

# Directory paths
tests_path = Path(__file__).resolve().parent
package_path = tests_path.resolve().parent.parent

class TestPaths(object):
    """Class to store paths to test data"""
    data_path = tests_path / "data"
    default_config_path = package_path / "config" / "config.json"
    demo_config_path_catalog = data_path / "test_config_file_dataset.json"
    demo_config_path_dataset = data_path / "test_config_file_catalog.json"
    catalog_metadata_dataset1 = data_path / "catalog_metadata_dataset_valid.jsonl"
    catalog_metadata_dataset2 = data_path / "catalog_metadata_dataset_valid2.jsonl"
    catalog_metadata_valid_invalid = data_path / "catalog_metadata_valid_invalid.jsonl"


@pytest.fixture
def test_data():
    """Paths to test data"""
    return TestPaths()


@pytest.fixture
def demo_catalog(tmp_path, test_data) -> WebCatalog:
    """A simple WebCatalog instance with no added metadata"""
    catalog_path = tmp_path / "test_catalog"
    catalog = WebCatalog(
        location=catalog_path,
        config_file=str(test_data.demo_config_path_catalog),
        catalog_action="create",
    )
    catalog.create()
    return catalog


