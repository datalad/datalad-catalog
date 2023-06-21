from datalad.support.exceptions import InsufficientArgumentsError
from datalad.tests.utils_pytest import (
    assert_in_results,
    assert_result_count,
)
from datalad_catalog.catalog import Catalog
import datalad_catalog.constants as cnst
from datalad_catalog.add import Add
from datalad_catalog.get import Get
from datalad_catalog.utils import read_json_file

import io
import json
from pathlib import Path
import pytest


from datalad_next.constraints.exceptions import CommandParametrizationError

catalog_add = Add()
catalog_get = Get()
catalog_cmd = Catalog()


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
        catalog_get(catalog=demo_catalog,
                    property='metadata')
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog,
                    property='metadata',
                    dataset_id='1234')
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog,
                    property='metadata',
                    dataset_version='v1')
    # for property=metadata, require record_type if record_path is specified
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog,
                    property='metadata',
                    dataset_id='1234',
                    dataset_version='v1',
                    record_path='subdir/bla')
    # for property=metadata, require record_path for record_type in ('directory', 'file')
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog,
                    property='metadata',
                    dataset_id='1234',
                    dataset_version='v1',
                    record_type='directory')
    # for property=config, require both dataset_id and dataset_version, or neither
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog,
                    property='config',
                    dataset_id='1234')
    with pytest.raises(CommandParametrizationError):
        catalog_get(catalog=demo_catalog,
                    property='config',
                    dataset_version='v1')


def test_get_tree(demo_catalog):
    """Tests for property: tree"""
    # placeholder test until the tree functionality is implemented
    res = catalog_get(catalog=demo_catalog,
                      property='tree',
                      on_failure="ignore",
                      return_type="list",)
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
    res = catalog_get(catalog=demo_catalog,
                      property='home',
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="home",
        status="impossible",
        path=demo_catalog.location,
    )
    # set home spec of demo catalog
    # TODO: this is currently done via old API command and should
    # be updated once the 'datalad_catalog.set' module is implemented
    # Extra info: currently seeting the super id and version on a catalog
    # is possible even if a dataset with the specified id and version
    # is not contained in the catalog. This is obviously wrong, and will
    # be fixed with the new 'set' command.
    home_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    home_version = "dae38cf901995aace0dde5346515a0134f919523"
    catalog_cmd(
        "set-super",
        catalog_dir=str(demo_catalog.location),
        dataset_id=home_id,
        dataset_version=home_version,
    )
    # test existing home spec
    res = catalog_get(catalog=demo_catalog,
                      property='home',
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="home",
        status="ok",
        path=demo_catalog.location,
    )
    assert 'home' in res[0]
    assert res[0]['home'] is not None
    assert res[0]['home']['dataset_id'] == home_id
    assert res[0]['home']['dataset_version'] == home_version


def test_get_metadata(demo_catalog, test_data):
    """Tests for property: metadata"""
    # test metadata at non-existing dataset
    res = catalog_get(catalog=demo_catalog,
                      property='metadata',
                      dataset_id='test_id',
                      dataset_version='test_version',
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="impossible",
        path=demo_catalog.location,
    )
    assert res[0]['metadata'] is None
    # add dataset-level metadata
    catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    # now test metadata at existing dataset
    ds_meta = read_json_file(test_data.catalog_metadata_dataset1)
    res = catalog_get(catalog=demo_catalog,
                      property='metadata',
                      dataset_id=ds_meta['dataset_id'],
                      dataset_version=ds_meta['dataset_version'],
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="ok",
        path=demo_catalog.location,
    )
    assert 'metadata' in res[0]
    assert res[0]['metadata'] is not None
    assert res[0]['metadata']['dataset_id'] == ds_meta['dataset_id']
    assert res[0]['metadata']['dataset_version'] == ds_meta['dataset_version']
    # add file-level metadata
    catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_file_single,
        on_failure="ignore",
        return_type="list",
    )
    # now test metadata at existing directory + file
    file_meta = read_json_file(test_data.catalog_metadata_file_single)
    file_path = file_meta['path']
    dir_path = str(Path(file_path).parent)
    res = catalog_get(catalog=demo_catalog,
                      property='metadata',
                      dataset_id=file_meta['dataset_id'],
                      dataset_version=file_meta['dataset_version'],
                      record_type='directory',
                      record_path=dir_path,
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="ok",
        path=demo_catalog.location,
    )
    assert 'metadata' in res[0]
    assert res[0]['metadata'] is not None
    assert res[0]['metadata']['dataset_id'] == file_meta['dataset_id']
    assert res[0]['metadata']['dataset_version'] == file_meta['dataset_version']
    res = catalog_get(catalog=demo_catalog,
                      property='metadata',
                      dataset_id=file_meta['dataset_id'],
                      dataset_version=file_meta['dataset_version'],
                      record_type='file',
                      record_path=file_path,
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="ok",
        path=demo_catalog.location,
    )
    assert 'metadata' in res[0]
    assert res[0]['metadata'] is not None
    assert res[0]['metadata']['dataset_id'] == file_meta['dataset_id']
    assert res[0]['metadata']['dataset_version'] == file_meta['dataset_version']
    # and lastly test a nonexisting dir
    res = catalog_get(catalog=demo_catalog,
                      property='metadata',
                      dataset_id=file_meta['dataset_id'],
                      dataset_version=file_meta['dataset_version'],
                      record_type='directory',
                      record_path=file_path + '/blabla',
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="metadata",
        status="impossible",
        path=demo_catalog.location,
    )
    assert res[0]['metadata'] is None


def test_get_config(demo_catalog_default_config, demo_catalog, test_data):
    """Tests for property: config"""
    # test default config on catalog-level
    default_config = read_json_file(test_data.default_config_path)
    res = catalog_get(catalog=demo_catalog_default_config,
                      property='config',
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="config",
        status="ok",
        path=demo_catalog_default_config.location,
    )
    assert 'config' in res[0]
    assert default_config == res[0]['config']
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
    # TODO: this fails. For some reason, the file is not created during
    # the add operation. A similar test succeeds in 'test_config.py' but that
    # code uses the old API 'datalad catalog add'.
    # Check differences between old and new add to find issue.
    config_file_path = demo_catalog_default_config.location /\
        "metadata" / ds_meta['dataset_id'] / ds_meta['dataset_version'] /\
            "config.json"
    assert config_file_path.exists()
    # - Dataset config attribute should exist
    assert hasattr(demo_catalog_default_config, "dataset_config")
    # - Dataset config attribute should have correct dataset-specific content
    assert demo_catalog_default_config.dataset_config is not None
    assert (
        demo_catalog_default_config.dataset_config[cnst.CATALOG_NAME]
        == "DataLad Catalog Config Test Dataset"
    )
    res = catalog_get(catalog=demo_catalog_default_config,
                      property='config',
                      dataset_id=ds_meta['dataset_id'],
                      dataset_version=ds_meta['dataset_version'],
                      on_failure="ignore",
                      return_type="list",)
    assert_in_results(
        res,
        action="catalog_get",
        action_property="config",
        status="ok",
        path=demo_catalog_default_config.location,
    )
    assert 'config' in res[0]
    print(res[0]['config'])
