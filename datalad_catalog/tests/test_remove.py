from datalad.tests.utils_pytest import (
    assert_in_results,
)
from datalad_catalog.add import Add
from datalad_catalog.remove import Remove
from datalad_catalog.utils import read_json_file

from pathlib import Path
import pytest


from datalad_next.constraints.exceptions import CommandParametrizationError

catalog_add = Add()
catalog_remove = Remove()


def test_args(demo_catalog, test_data):
    """The catalog, id, version, and reckless arguments are required"""
    with pytest.raises(CommandParametrizationError):
        catalog_remove()

    with pytest.raises(CommandParametrizationError):
        catalog_remove(catalog=demo_catalog)

    with pytest.raises(CommandParametrizationError):
        catalog_remove(catalog=demo_catalog)

    with pytest.raises(CommandParametrizationError):
        catalog_remove(catalog=demo_catalog, dataset_id="123")

    with pytest.raises(CommandParametrizationError):
        catalog_remove(catalog=demo_catalog, dataset_version="abc")

    with pytest.raises(CommandParametrizationError):
        catalog_remove(
            catalog=demo_catalog, dataset_id="123", dataset_version="abc"
        )


def test_remove_outofcatalog(demo_catalog, test_data):
    """Tests for property: home"""
    # 1. Test when no home page already set, dataset NOT in catalog
    # test without reckless=overwrite
    res = catalog_remove(
        catalog=demo_catalog,
        dataset_id="id_not_in_ctalog",
        dataset_version="version_not_in_catalog",
        reckless=True,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_remove",
        status="impossible",
        path=demo_catalog.location,
    )


def test_remove_outofcatalog(demo_catalog, test_data):
    """Test when removing a nonexisting record"""
    # 1. Test when no home page already set, dataset NOT in catalog
    # test without reckless=overwrite
    res = catalog_remove(
        catalog=demo_catalog,
        dataset_id="id_not_in_ctalog",
        dataset_version="version_not_in_catalog",
        reckless=True,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_remove",
        status="impossible",
        path=demo_catalog.location,
    )


def test_remove(demo_catalog, test_data):
    """Test when removing an existing record"""
    res = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )
    mdata = read_json_file(test_data.catalog_metadata_dataset1)
    mdata_id = mdata.get("dataset_id")
    mdata_v = mdata.get("dataset_version")
    res = catalog_remove(
        catalog=demo_catalog,
        dataset_id=mdata_id,
        dataset_version=mdata_v,
        reckless=True,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_remove",
        status="ok",
        path=demo_catalog.location,
    )
    id_path = Path(demo_catalog.location) / "metadata" / mdata_id
    v_path = id_path / mdata_v
    assert not id_path.exists()
    assert not v_path.exists()


def test_remove_version_only(demo_catalog, test_data):
    """Test when removing an existing record, version only"""
    res = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )

    mdata = read_json_file(test_data.catalog_metadata_dataset1)
    mdata_id = mdata.get("dataset_id")
    mdata_v = mdata.get("dataset_version")
    id_path = Path(demo_catalog.location) / "metadata" / mdata_id
    v_path = id_path / mdata_v
    other_v_path = id_path / "version_to_remain"
    other_v_path.mkdir()

    res = catalog_remove(
        catalog=demo_catalog,
        dataset_id=mdata_id,
        dataset_version=mdata_v,
        reckless=True,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_remove",
        status="ok",
        path=demo_catalog.location,
    )
    assert not v_path.exists()
    assert id_path.exists()
    assert other_v_path.exists()
