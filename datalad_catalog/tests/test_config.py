from datalad_catalog.add import Add
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import WebCatalog
from datalad_catalog.node import Node

from pathlib import Path
import pytest


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
    ctlg = WebCatalog(
        location=catalog_path,
    )
    ctlg.create(config_file=str(demo_config_path_yml))
    return ctlg


@pytest.fixture
def demo_catalog_with_config_json(tmp_path):
    catalog_path = tmp_path / "demo_catalog_with_config_json"
    ctlg = WebCatalog(
        location=catalog_path,
    )
    ctlg.create(config_file=str(demo_config_path_json))
    return ctlg


@pytest.fixture
def demo_catalog_without_config(tmp_path):
    catalog_path = tmp_path / "demo_catalog_without_config"
    ctlg = WebCatalog(
        location=catalog_path,
    )
    ctlg.create(config_file=None)
    return ctlg


def test_config_with_file_yml(demo_catalog_with_config_yml):
    assert demo_catalog_with_config_yml.config_path == demo_config_path_yml
    assert hasattr(demo_catalog_with_config_yml, "config")
    assert demo_catalog_with_config_yml.config is not None
    assert (
        demo_catalog_with_config_yml.config[CATALOG_NAME]
        == "DataLad Catalog Config Test"
    )


def test_config_with_file_json(demo_catalog_with_config_json):
    assert demo_catalog_with_config_json.config_path == demo_config_path_json
    assert hasattr(demo_catalog_with_config_json, "config")
    assert demo_catalog_with_config_json.config is not None
    assert (
        demo_catalog_with_config_json.config[CATALOG_NAME]
        == "DataLad Catalog Config Test"
    )


def test_config_without_file(demo_catalog_without_config):
    assert demo_catalog_without_config.config_path == default_config_path
    assert hasattr(demo_catalog_without_config, "config")
    assert demo_catalog_without_config.config is not None
    assert demo_catalog_without_config.config[CATALOG_NAME] == "DataCat"


def test_dataset_config(tmp_path):
    """"""
    catalog_add = Add()
    # 0. Create catalog with custom config file
    catalog_path = tmp_path / "new_catalog"
    ctlg = WebCatalog(
        location=catalog_path,
    )
    ctlg.create(config_file=str(demo_config_path_json))
    # 1. Test dataset add with dataset-specific config file
    catalog_add(
        catalog=ctlg,
        metadata=str(metadata_path1),
        config_file=demo_config_path_dataset,
    )
    # - Dataset config file should be created
    d_id = _get_value_from_file(metadata_path1, "dataset_id")
    d_v = _get_value_from_file(metadata_path1, "dataset_version")
    config_file_path = catalog_path / "metadata" / d_id / d_v / "config.json"
    assert config_file_path.exists()
    # - Grab Node instance
    node_instance = Node(
        catalog=ctlg,
        type="dataset",
        dataset_id=d_id,
        dataset_version=d_v,
        node_path=None,
    )
    cfg = node_instance.get_config()
    # - config attribute should have correct dataset-specific content
    assert cfg is not None
    assert cfg.get("source") == "dataset"
    assert (
        cfg.get("config").get(CATALOG_NAME)
        == "DataLad Catalog Config Test Dataset"
    )
    # 2. Next, test dataset add with NO CONFIG
    catalog_add(
        catalog=ctlg,
        metadata=str(metadata_path2),
    )
    # - Dataset config file should NOT be created
    d_id = _get_value_from_file(metadata_path2, "dataset_id")
    d_v = _get_value_from_file(metadata_path2, "dataset_version")
    config_file_path = catalog_path / "metadata" / d_id / d_v / "config.json"
    assert not config_file_path.exists()
    # - Grab webcatalog instance
    # - Grab Node instance
    node_instance = Node(
        catalog=ctlg,
        type="dataset",
        dataset_id=d_id,
        dataset_version=d_v,
        node_path=None,
    )
    cfg = node_instance.get_config()
    # config attribute should exist and be correct and from correct source
    assert cfg is not None
    assert cfg.get("source") == "catalog"
    assert cfg.get("config").get(CATALOG_NAME) == "DataLad Catalog Config Test"


def _get_value_from_file(metadata_path, key):
    meta_dict = read_json_file(metadata_path)
    return meta_dict[key]
