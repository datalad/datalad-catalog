from pathlib import Path

import pytest

from datalad_catalog.catalog import Catalog
from datalad_catalog.meta_item import MetaItem
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import WebCatalog, Node


CATALOG_NAME = "catalog_name"

tests_path = Path(__file__).resolve().parent
data_path = tests_path / "data"
demo_config_path_yml = data_path / "test_config_file.yml"
demo_config_path_json = data_path / "test_config_file.json"
demo_config_path_dataset = data_path / "test_config_file_dataset.json"
metadata_path1 = data_path / "catalog_metadata_dataset.jsonl"
metadata_path2 = data_path / "catalog_metadata_dataset2.jsonl"
package_path = Path(__file__).resolve().parent.parent
default_config_path = package_path / "config" / "config.json"


@pytest.fixture
def demo_catalog_with_config_yml(tmp_path):
    catalog_path = tmp_path / "demo_catalog_with_config_yml"
    return WebCatalog(
        location=catalog_path,
        config_file=str(demo_config_path_yml),
        catalog_action="create",
    )


@pytest.fixture
def demo_catalog_with_config_json(tmp_path):
    catalog_path = tmp_path / "demo_catalog_with_config_json"
    return WebCatalog(
        location=catalog_path,
        config_file=str(demo_config_path_json),
        catalog_action="create",
    )


@pytest.fixture
def demo_catalog_without_config(tmp_path):
    catalog_path = tmp_path / "demo_catalog_without_config"
    return WebCatalog(
        location=catalog_path, config_file=None, catalog_action="create"
    )


def test_config_with_file_yml(demo_catalog_with_config_yml):
    assert (
        demo_catalog_with_config_yml.catalog_config_path == demo_config_path_yml
    )
    assert hasattr(demo_catalog_with_config_yml, "catalog_config")
    assert demo_catalog_with_config_yml.catalog_config is not None
    assert (
        demo_catalog_with_config_yml.catalog_config[CATALOG_NAME]
        == "DataLad Catalog Config Test"
    )


def test_config_with_file_json(demo_catalog_with_config_json):
    assert (
        demo_catalog_with_config_json.catalog_config_path
        == demo_config_path_json
    )
    assert hasattr(demo_catalog_with_config_json, "catalog_config")
    assert demo_catalog_with_config_json.catalog_config is not None
    assert (
        demo_catalog_with_config_json.catalog_config[CATALOG_NAME]
        == "DataLad Catalog Config Test"
    )


def test_config_without_file(demo_catalog_without_config):
    assert (
        demo_catalog_without_config.catalog_config_path == default_config_path
    )
    assert hasattr(demo_catalog_without_config, "catalog_config")
    assert demo_catalog_without_config.catalog_config is not None
    assert demo_catalog_without_config.catalog_config[CATALOG_NAME] == "DataCat"


def test_dataset_config(tmp_path):
    """"""
    # 0. Create catalog with custom config file
    catalog_path = tmp_path / "new_catalog"
    catalog = Catalog()
    catalog(
        catalog_action="create",
        catalog_dir=catalog_path,
        config_file=demo_config_path_json,
    )
    # 1. Test dataset add with dataset-specific config file
    catalog(
        catalog_action="add",
        catalog_dir=catalog_path,
        metadata=str(metadata_path1),
        config_file=demo_config_path_dataset,
    )
    # - Dataset config file should be created
    d_id = _get_value_from_file(metadata_path1, "dataset_id")
    d_v = _get_value_from_file(metadata_path1, "dataset_version")
    config_file_path = catalog_path / "metadata" / d_id / d_v / "config.json"
    assert config_file_path.exists()
    # - Grab webcatalog instance
    ctlg = WebCatalog(
        catalog_path,
        None,
        None,
        demo_config_path_dataset,
        "add",
    )
    # - Dataset config attribute should exist
    assert hasattr(ctlg, "dataset_config")
    # - Dataset config attribute should have correct dataset-specific content
    assert ctlg.dataset_config is not None
    assert (
        ctlg.dataset_config[CATALOG_NAME]
        == "DataLad Catalog Config Test Dataset"
    )
    # 2. Next, test dataset add with NO CONFIG
    catalog(
        catalog_action="add",
        catalog_dir=catalog_path,
        metadata=metadata_path2,
        config_file=None,
    )
    # - Dataset config file should NOT be created
    d_id = _get_value_from_file(metadata_path2, "dataset_id")
    d_v = _get_value_from_file(metadata_path2, "dataset_version")
    config_file_path = catalog_path / "metadata" / d_id / d_v / "config.json"
    assert not config_file_path.exists()
    # - Grab webcatalog instance
    ctlg = WebCatalog(
        catalog_path,
        None,
        None,
        None,
        "add",
    )
    # - Grab Node instance
    nd = Node(
        catalog=ctlg, type="dataset", dataset_id=d_id, dataset_version=d_v
    )
    # config attribute should exist on node instance
    assert hasattr(nd, "config")
    # Config attribute should be set from catalog level (here, from specific file)
    assert nd.config is not None
    assert nd.config[CATALOG_NAME] == "DataLad Catalog Config Test"


def _get_value_from_file(metadata_path, key):
    meta_dict = read_json_file(metadata_path)
    return meta_dict[key]
