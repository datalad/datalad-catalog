import hashlib
import json
import os
from pathlib import Path

import pytest

from datalad_catalog import constants as cnst
from datalad_catalog.meta_item import MetaItem
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import (
    Node,
    WebCatalog,
    getNode,
)

tests_path = Path(__file__).resolve().parent
data_path = tests_path / "data"


@pytest.fixture
def demo_metadata_item():
    metadata_path = data_path / "catalog_metadata_dataset.json"
    return read_json_file(metadata_path)


@pytest.fixture
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    return WebCatalog(location=catalog_path)


def test_translate_dataset(demo_metadata_item: dict, demo_catalog: WebCatalog):
    """ """
    Node._instances = {}
    demo_catalog.config = {"property_source": {"dataset": {}}}
    metatest = MetaItem(demo_catalog, demo_metadata_item)
    assert len(Node._instances) == 1
    new_node = [
        Node._instances[n]
        for n in Node._instances
        if Node._instances[n].dataset_id == demo_metadata_item[cnst.DATASET_ID]
        and Node._instances[n].dataset_version
        == demo_metadata_item[cnst.DATASET_VERSION]
    ]
    assert len(new_node) == 1
    fn = new_node[0].get_location()
    new_node[0].write_to_file()
    translated_metadata = read_json_file(fn)
    for key in translated_metadata:
        if not bool(translated_metadata[key]):
            continue
        assert key in demo_metadata_item
        assert demo_metadata_item[key] == translated_metadata[key]
