

from pathlib import Path
import pytest
from datalad_catalog.constants import (
    package_path,
    tests_path,
)
from datalad_catalog.webcatalog import WebCatalog

class TestPaths(object):
    """Class to store paths to test data"""
    data_path = tests_path / "data"
    default_config_path = package_path / "config" / "config.json"
    demo_config_path_catalog = data_path / "test_config_file_catalog.json"
    demo_config_path_dataset = data_path / "test_config_file_dataset.json"
    catalog_metadata_dataset1 = data_path / "catalog_metadata_dataset_valid.jsonl"
    catalog_metadata_dataset2 = data_path / "catalog_metadata_dataset_valid2.jsonl"
    catalog_metadata_file1 = data_path / "catalog_metadata_file_valid.jsonl"
    catalog_metadata_file_single = data_path / "catalog_metadata_file_valid_single.jsonl"
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
    )
    catalog.create(config_file=str(test_data.demo_config_path_catalog))
    return catalog

@pytest.fixture
def demo_catalog_default_config(tmp_path) -> WebCatalog:
    """A simple WebCatalog instance with no added metadata
    and no config specified"""
    catalog_path = tmp_path / "test_catalog_wo_config"
    catalog = WebCatalog(
        location=catalog_path,
    )
    catalog.create()
    return catalog


