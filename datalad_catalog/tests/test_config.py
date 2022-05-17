from pathlib import Path
import pytest
from ..utils import read_json_file
from ..webcatalog import WebCatalog

CATALOG_NAME = "catalog_name"

tests_path = Path(__file__).resolve().parent
data_path = tests_path / 'data'
demo_config_path = data_path / 'test_config_file.yml'

package_path = Path(__file__).resolve().parent.parent
default_config_path = package_path / 'templates' / 'config.yml'

@pytest.fixture
def demo_metadata_item():
    metadata_path = data_path / 'catalog_metadata_dataset.json'
    return read_json_file(metadata_path)

@pytest.fixture
def demo_catalog_with_config(tmp_path):
    catalog_path = tmp_path / "demo_catalog_with_config"
    return WebCatalog(location=catalog_path, config_file=str(demo_config_path))

@pytest.fixture
def demo_catalog_without_config(tmp_path):
    catalog_path = tmp_path / "demo_catalog_without_config"
    return WebCatalog(location=catalog_path, config_file=None)


def test_config_with_file(tmp_path, demo_catalog_with_config):
    assert demo_catalog_with_config.config_path == demo_config_path
    assert hasattr(demo_catalog_with_config, 'config')
    assert demo_catalog_with_config.config is not None
    assert demo_catalog_with_config.config[CATALOG_NAME] == "DataLad Catalog Config Test"

def test_config_without_file(tmp_path, demo_catalog_without_config):
    assert demo_catalog_without_config.config_path == default_config_path
    assert hasattr(demo_catalog_without_config, 'config')
    assert demo_catalog_without_config.config is not None
    assert demo_catalog_without_config.config[CATALOG_NAME] == "DataCat"





# def test_translate_dataset(demo_metadata_item: dict, demo_catalog: WebCatalog):
#     """
#     """
#     metatest = MetaItem(demo_catalog, demo_metadata_item)
#     assert len(Node._instances) == 1
#     new_node = [Node._instances[n] for n in Node._instances if
#                 Node._instances[n].dataset_id == demo_metadata_item[cnst.DATASET_ID] and
#                 Node._instances[n].dataset_version == demo_metadata_item[cnst.DATASET_VERSION]]
#     assert len(new_node) == 1
#     fn = new_node[0].get_location()
#     new_node[0].write_to_file()
#     translated_metadata = read_json_file(fn)
#     assert demo_metadata_item == translated_metadata