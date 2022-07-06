from pathlib import Path

import pytest

from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import WebCatalog

CATALOG_NAME = "catalog_name"

tests_path = Path(__file__).resolve().parent
data_path = tests_path / "data"
demo_config_path_yml = data_path / "test_config_file.yml"
demo_config_path_json = data_path / "test_config_file.json"

package_path = Path(__file__).resolve().parent.parent
default_config_path = package_path / "config" / "config.json"


@pytest.fixture
def demo_metadata_item():
    metadata_path = data_path / "catalog_metadata_dataset.json"
    return read_json_file(metadata_path)


@pytest.fixture
def demo_catalog_with_config_yml(tmp_path):
    catalog_path = tmp_path / "demo_catalog_with_config_yml"
    return WebCatalog(
        location=catalog_path, config_file=str(demo_config_path_yml)
    )


@pytest.fixture
def demo_catalog_with_config_json(tmp_path):
    catalog_path = tmp_path / "demo_catalog_with_config_json"
    return WebCatalog(
        location=catalog_path, config_file=str(demo_config_path_json)
    )


@pytest.fixture
def demo_catalog_without_config(tmp_path):
    catalog_path = tmp_path / "demo_catalog_without_config"
    return WebCatalog(location=catalog_path, config_file=None)


def test_config_with_file_yml(tmp_path, demo_catalog_with_config_yml):
    assert demo_catalog_with_config_yml.config_path == demo_config_path_yml
    assert hasattr(demo_catalog_with_config_yml, "config")
    assert demo_catalog_with_config_yml.config is not None
    assert (
        demo_catalog_with_config_yml.config[CATALOG_NAME]
        == "DataLad Catalog Config Test"
    )


def test_config_with_file_json(tmp_path, demo_catalog_with_config_json):
    assert demo_catalog_with_config_json.config_path == demo_config_path_json
    assert hasattr(demo_catalog_with_config_json, "config")
    assert demo_catalog_with_config_json.config is not None
    assert (
        demo_catalog_with_config_json.config[CATALOG_NAME]
        == "DataLad Catalog Config Test"
    )


def test_config_without_file(tmp_path, demo_catalog_without_config):
    assert demo_catalog_without_config.config_path == default_config_path
    assert hasattr(demo_catalog_without_config, "config")
    assert demo_catalog_without_config.config is not None
    assert demo_catalog_without_config.config[CATALOG_NAME] == "DataCat"
