import pytest
from datalad_catalog.create import Create
from datalad.tests.utils_pytest import (
    assert_in_results,
)
from datalad_next.constraints.exceptions import CommandParametrizationError

catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/app.js",
    "assets/style.css",
    "artwork",
    "templates",
    "schema",
    "index.html",
    "config.json",
    "README.md",
]

catalog_create = Create()


def test_no_args(tmp_path):
    """At least the catalog argument is required"""
    with pytest.raises(CommandParametrizationError):
        catalog_create()


def test_create(tmp_path):
    """
    Test if catalog is created successfully given a path as single argument,
    where path does not yet exist
    """
    catalog_path = tmp_path / "test_catalog"
    res = catalog_create(catalog=catalog_path)
    assert_in_results(
        res,
        action="catalog_create",
        status="ok",
        path=catalog_path,
    )
    assert catalog_path.exists()
    assert catalog_path.is_dir()

    for p in catalog_paths:
        pth = catalog_path / p
        assert pth.exists()


def test_create_with_metadata(tmp_path, test_data):
    """
    Test if catalog is created successfully given a path that
    does not yet exist and some metadata as the input args
    """
    catalog_path = tmp_path / "test_catalog"
    res = catalog_create(
        catalog=catalog_path,
        metadata=test_data.catalog_metadata_dataset1,
    )
    assert_in_results(
        res,
        action="catalog_create",
        status="ok",
        path=catalog_path,
    )
    assert catalog_path.exists()
    assert catalog_path.is_dir()
    for p in catalog_paths:
        pth = catalog_path / p
        assert pth.exists()
    assert_in_results(
        res,
        action="catalog_add",
        status="ok",
        path=catalog_path,
    )


def test_create_at_existing_noncatalog(tmp_path):
    """
    Test if error is raised when create is used on an existing
    non-catalog directory
    """
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    with pytest.raises(CommandParametrizationError):
        catalog_create(catalog=dir_path)


def test_create_at_existing_catalog_noforce(demo_catalog):
    """
    Test if error is raised when create is used on an existing catalog
    """
    new_catalog_path = demo_catalog.location
    with pytest.raises(CommandParametrizationError):
        catalog_create(catalog=new_catalog_path)


def test_create_at_existing_catalog_force(demo_catalog):
    """
    Test if catalog is created when create is used on an existing catalog,
    together with force flag
    """
    new_catalog_path = demo_catalog.location
    res = catalog_create(catalog=new_catalog_path, force=True)
    assert_in_results(
        res,
        action="catalog_create",
        status="ok",
        path=new_catalog_path,
    )
    assert new_catalog_path.exists()
    assert new_catalog_path.is_dir()

    for p in catalog_paths:
        pth = new_catalog_path / p
        assert pth.exists()
