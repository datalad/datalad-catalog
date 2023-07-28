from datalad.tests.utils_pytest import (
    assert_in_results,
)
import datalad_catalog.constants as cnst
from datalad_catalog.add import Add
from datalad_catalog.get import Get
from datalad_catalog.node import Node
from datalad_catalog.set import Set
from datalad_catalog.utils import read_json_file

from datalad_next.constraints.exceptions import CommandParametrizationError

from pathlib import Path
import pytest

catalog_add = Add()
catalog_get = Get()
catalog_set = Set()


def test_arg_combinations(demo_catalog):
    """Test various incorrect combinations of arguments"""
    # no arguments
    with pytest.raises(CommandParametrizationError):
        catalog_get()
    # only catalog (no further positional/optional args)
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog)
    # for property=metadata, always require both dataset_id and dataset_version
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog, property="metadata")
    with pytest.raises(CommandParametrizationError):
        catalog_get(
            catalog=demo_catalog, property="metadata", dataset_id="1234"
        )
    with pytest.raises(CommandParametrizationError):
        catalog_get(
            catalog=demo_catalog, property="metadata", dataset_version="v1"
        )
    # for property=metadata, require record_type if record_path is specified
    with pytest.raises(CommandParametrizationError):
        catalog_get(
            catalog=demo_catalog,
            property="metadata",
            dataset_id="1234",
            dataset_version="v1",
            record_path="subdir/bla",
        )
    # for property=metadata, require record_path for record_type in ('directory', 'file')
    with pytest.raises(CommandParametrizationError):
        catalog_get(
            catalog=demo_catalog,
            property="metadata",
            dataset_id="1234",
            dataset_version="v1",
            record_type="directory",
        )
    # for property=config, require both dataset_id and dataset_version, or neither
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog, property="config", dataset_id="1234")
    with pytest.raises(CommandParametrizationError):
        catalog_get(
            catalog=demo_catalog, property="config", dataset_version="v1"
        )


def test_get_tree(demo_catalog):
    """Tests for property: tree"""
    # placeholder test until the tree functionality is implemented
    res = catalog_get(
        catalog=demo_catalog,
        property="tree",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="tree",
        status="error",
        path=demo_catalog.location,
    )


def test_get_home(demo_catalog, test_data):
    """Tests for property: home"""
    # test no home spec
    res = catalog_get(
        catalog=demo_catalog,
        property="home",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="home",
        status="impossible",
        path=demo_catalog.location,
    )
    # set home spec of demo catalog
    home_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    home_version = "dae38cf901995aace0dde5346515a0134f919523"
    catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id=home_id,
        dataset_version=home_version,
        on_failure="ignore",
        return_type="list",
    )
    # test existing home spec
    res = catalog_get(
        catalog=demo_catalog,
        property="home",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="home",
        status="ok",
        path=demo_catalog.location,
    )
    assert "output" in res[0]
    assert res[0]["output"] is not None
    assert res[0]["output"][cnst.DATASET_ID] == home_id
    assert res[0]["output"][cnst.DATASET_VERSION] == home_version


def test_get_metadata(demo_catalog, test_data):
    """Tests for property: metadata"""
    # test metadata at non-existing dataset
    res = catalog_get(
        catalog=demo_catalog,
        property="metadata",
        dataset_id="test_id",
        dataset_version="test_version",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="impossible",
        path=demo_catalog.location,
    )
    assert res[0]["output"] is None
    # add dataset-level metadata
    catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    # now test metadata at existing dataset
    ds_meta = read_json_file(test_data.catalog_metadata_dataset1)
    res = catalog_get(
        catalog=demo_catalog,
        property="metadata",
        dataset_id=ds_meta[cnst.DATASET_ID],
        dataset_version=ds_meta[cnst.DATASET_VERSION],
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="ok",
        path=demo_catalog.location,
    )
    assert "output" in res[0]
    assert res[0]["output"] is not None
    assert res[0]["output"][cnst.DATASET_ID] == ds_meta[cnst.DATASET_ID]
    assert (
        res[0]["output"][cnst.DATASET_VERSION] == ds_meta[cnst.DATASET_VERSION]
    )
    # add file-level metadata
    catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_file_single,
        on_failure="ignore",
        return_type="list",
    )
    # now test metadata at existing directory + file
    file_meta = read_json_file(test_data.catalog_metadata_file_single)
    file_path = file_meta["path"]
    dir_path = str(Path(file_path).parent)
    res = catalog_get(
        catalog=demo_catalog,
        property="metadata",
        dataset_id=file_meta[cnst.DATASET_ID],
        dataset_version=file_meta[cnst.DATASET_VERSION],
        record_type="directory",
        record_path=dir_path,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="ok",
        path=demo_catalog.location,
    )
    assert "output" in res[0]
    assert res[0]["output"] is not None
    assert res[0]["output"][cnst.DATASET_ID] == file_meta[cnst.DATASET_ID]
    assert (
        res[0]["output"][cnst.DATASET_VERSION]
        == file_meta[cnst.DATASET_VERSION]
    )
    res = catalog_get(
        catalog=demo_catalog,
        property="metadata",
        dataset_id=file_meta[cnst.DATASET_ID],
        dataset_version=file_meta[cnst.DATASET_VERSION],
        record_type="file",
        record_path=file_path,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="ok",
        path=demo_catalog.location,
    )
    assert "output" in res[0]
    assert res[0]["output"] is not None
    assert res[0]["output"][cnst.DATASET_ID] == file_meta[cnst.DATASET_ID]
    assert (
        res[0]["output"][cnst.DATASET_VERSION]
        == file_meta[cnst.DATASET_VERSION]
    )
    # and lastly test a nonexisting dir
    res = catalog_get(
        catalog=demo_catalog,
        property="metadata",
        dataset_id=file_meta[cnst.DATASET_ID],
        dataset_version=file_meta[cnst.DATASET_VERSION],
        record_type="directory",
        record_path=file_path + "/blabla",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="impossible",
        path=demo_catalog.location,
    )
    assert res[0]["output"] is None


def test_get_config(demo_catalog_default_config, demo_catalog, test_data):
    """Tests for property: config"""
    # test default config on catalog-level
    default_config = read_json_file(test_data.default_config_path)
    res = catalog_get(
        catalog=demo_catalog_default_config,
        property="config",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="config",
        status="ok",
        path=demo_catalog_default_config.location,
    )
    assert "output" in res[0]
    assert default_config == res[0]["output"]
    # test dataset-level config after adding to same catalog with default config
    dataset_config = read_json_file(test_data.demo_config_path_dataset)
    ds_meta = read_json_file(test_data.catalog_metadata_dataset1)
    catalog_add(
        catalog=demo_catalog_default_config,
        metadata=test_data.catalog_metadata_dataset1,
        config_file=str(test_data.demo_config_path_dataset),
        on_failure="ignore",
        return_type="list",
    )
    # - Dataset config file should exist
    config_file_path = (
        demo_catalog_default_config.location
        / "metadata"
        / ds_meta[cnst.DATASET_ID]
        / ds_meta[cnst.DATASET_VERSION]
        / "config.json"
    )
    assert config_file_path.exists()
    # - config attribute should exist on Node
    node_instance = Node(
        catalog=demo_catalog_default_config,
        dataset_id=ds_meta[cnst.DATASET_ID],
        dataset_version=ds_meta[cnst.DATASET_VERSION],
        type="dataset",
    )
    assert hasattr(node_instance, "config")
    # - Dataset config attribute should have correct dataset-specific content
    assert node_instance.config is not None
    assert (
        node_instance.config[cnst.CATALOG_NAME]
        == "DataLad Catalog Config Test Dataset"
    )
    res = catalog_get(
        catalog=demo_catalog_default_config,
        property="config",
        dataset_id=ds_meta[cnst.DATASET_ID],
        dataset_version=ds_meta[cnst.DATASET_VERSION],
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_get",
        action_property="config",
        status="ok",
        path=demo_catalog_default_config.location,
    )
    assert "output" in res[0]
