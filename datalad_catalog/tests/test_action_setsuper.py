import json

import pytest
from datalad.support.exceptions import InsufficientArgumentsError

from datalad_catalog import constants as cnst
from datalad_catalog import utils
from datalad_catalog.catalog import Catalog
from datalad_catalog.webcatalog import WebCatalog

catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/vue_app.js",
    "assets/style.css",
    "artwork",
    "index.html",
]


@pytest.fixture
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    test_catalog = Catalog()
    test_catalog("create", catalog_dir=catalog_path)
    return (test_catalog, catalog_path)


def test_setsuper(tmp_path, demo_catalog):
    """
    Test if, given dataset id and version, the superdataset file of a catalog
    is created with the correct content
    """
    test_catalog = demo_catalog[0]
    catalog_path = demo_catalog[1]
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_catalog(
        "set-super",
        catalog_dir=catalog_path,
        dataset_id=test_ds_id,
        dataset_version=test_ds_version,
    )
    super_path = catalog_path / "metadata" / "super.json"
    assert super_path.exists()
    assert super_path.is_file()
    super_json = {
        cnst.DATASET_ID: test_ds_id,
        cnst.DATASET_VERSION: test_ds_version,
    }
    read_json = utils.read_json_file(super_path)
    assert super_json == read_json


def test_setsuper_without_id(tmp_path, demo_catalog):
    """
    Test if the correct error is raised when set-super is called without dataset_id
    """
    test_catalog = demo_catalog[0]
    catalog_path = demo_catalog[1]
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    partial_error_msg = "Dataset ID and/or VERSION missing"
    with pytest.raises(InsufficientArgumentsError, match=partial_error_msg):
        test_catalog(
            "set-super",
            catalog_dir=catalog_path,
            dataset_version=test_ds_version,
        )


def test_setsuper_without_version(tmp_path, demo_catalog):
    """
    Test if the correct error is raised when set-super is called without dataset_version
    """
    test_catalog = demo_catalog[0]
    catalog_path = demo_catalog[1]
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    partial_error_msg = "Dataset ID and/or VERSION missing"
    with pytest.raises(InsufficientArgumentsError, match=partial_error_msg):
        test_catalog(
            "set-super", catalog_dir=catalog_path, dataset_id=test_ds_id
        )
