from datalad.tests.utils_pytest import (
    assert_in_results,
    assert_result_count,
)
import datalad_catalog.constants as cnst
from datalad_catalog.add import Add
from datalad_catalog.set import Set
from datalad_catalog.utils import read_json_file

from datalad_next.constraints.exceptions import CommandParametrizationError

import pytest

catalog_add = Add()
catalog_set = Set()


def test_arg_combinations(demo_catalog):
    """Test various incorrect combinations of arguments"""
    # no arguments
    with pytest.raises(CommandParametrizationError):
        catalog_set()
    # only catalog (no further positional/optional args)
    with pytest.raises(CommandParametrizationError):
        catalog_set(catalog=demo_catalog)
    # for property=home, always require both dataset_id and dataset_version
    with pytest.raises(CommandParametrizationError):
        catalog_set(catalog=demo_catalog, property="home")
    with pytest.raises(CommandParametrizationError):
        catalog_set(catalog=demo_catalog, property="home", dataset_id="1234")
    with pytest.raises(CommandParametrizationError):
        catalog_set(catalog=demo_catalog, property="home", dataset_version="v1")


def test_set_config(demo_catalog):
    """Tests for property: config"""
    # placeholder test until the tree functionality is implemented
    res = catalog_set(
        catalog=demo_catalog,
        property="config",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="config",
        status="error",
        path=demo_catalog.location,
    )


def test_set_home(demo_catalog, test_data):
    """Tests for property: home"""
    # 1. Test when no home page already set, dataset in catalog
    # First add a dataset to the catalog
    catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    # get test metadata to access id and version
    ds_meta = read_json_file(test_data.catalog_metadata_dataset1)
    # set home page
    res = catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id=ds_meta[cnst.DATASET_ID],
        dataset_version=ds_meta[cnst.DATASET_VERSION],
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="home",
        status="ok",
        path=demo_catalog.location,
        home={
            cnst.DATASET_ID: ds_meta[cnst.DATASET_ID],
            cnst.DATASET_VERSION: ds_meta[cnst.DATASET_VERSION],
        },
    )
    # 3. Test when home page already set: reckless or not
    # first add another dataset
    catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset2,
        on_failure="ignore",
        return_type="list",
    )
    # get new test metadata to access id and version
    ds_meta2 = read_json_file(test_data.catalog_metadata_dataset2)
    # set home page without overwrite
    res = catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id=ds_meta2[cnst.DATASET_ID],
        dataset_version=ds_meta2[cnst.DATASET_VERSION],
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="home",
        status="impossible",
        path=demo_catalog.location,
    )
    # set home page WITH overwrite
    res = catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id=ds_meta2[cnst.DATASET_ID],
        dataset_version=ds_meta2[cnst.DATASET_VERSION],
        reckless="overwrite",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="home",
        status="ok",
        path=demo_catalog.location,
        home={
            cnst.DATASET_ID: ds_meta2[cnst.DATASET_ID],
            cnst.DATASET_VERSION: ds_meta2[cnst.DATASET_VERSION],
        },
    )
    assert_result_count(
        res,
        1,
        action="catalog_set",
        action_property="home",
    )


def test_set_home_outofcatalog(demo_catalog, test_data):
    """Tests for property: home"""
    # 1. Test when no home page already set, dataset NOT in catalog
    # test without reckless=overwrite
    res = catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id="id_not_in_ctalog",
        dataset_version="version_not_in_ctalog",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="home",
        status="impossible",
        path=demo_catalog.location,
    )
    # test WITH reckless=overwrite
    res = catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id="id_not_in_ctalog",
        dataset_version="version_not_in_ctalog",
        reckless="overwrite",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="home",
        status="ok",
        path=demo_catalog.location,
        home={
            cnst.DATASET_ID: "id_not_in_ctalog",
            cnst.DATASET_VERSION: "version_not_in_ctalog",
        },
    )
    assert_result_count(
        res,
        1,
        action="catalog_set",
        action_property="home",
    )
    # 2. Test when home page already set, dataset NOT in catalog
    # test WITH reckless=overwrite
    res = catalog_set(
        catalog=demo_catalog,
        property="home",
        dataset_id="bla",
        dataset_version="bla",
        reckless="overwrite",
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_set",
        action_property="home",
        status="ok",
        path=demo_catalog.location,
        home={cnst.DATASET_ID: "bla", cnst.DATASET_VERSION: "bla"},
    )
    assert_result_count(
        res,
        1,
        action="catalog_set",
        action_property="home",
    )
