
from ..webcatalog import WebCatalog
from ..catalog import Catalog
import pytest
from datalad.support.exceptions import InsufficientArgumentsError

# catalog_paths = [
#     'assets/md5-2.3.0.js',
#     'assets/vue_app.js',
#     'assets/style.css',
#     'artwork',
#     'index.html']

catalog_paths = [
    'assets/md5-2.3.0.js',
    'assets/vue_app.js',
    'assets/style.css',
    'artwork',
    'index.html',
    'config.json']

def test_create(tmp_path):
    """
    Test if catalog is created successfully given a path as single argument,
    where path does not yet exist
    """
    catalog_path = tmp_path / "test_catalog"
    test_catalog = Catalog()
    test_catalog('create', catalog_dir=catalog_path)

    assert catalog_path.exists()
    assert catalog_path.is_dir()

    for p in catalog_paths:
        pth = catalog_path / p
        assert pth.exists()

def test_create_at_existing_noncatalog(tmp_path):
    """
    Test if error is raised when create action is used on an existing
    non-catalog directory
    """
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    test_catalog = Catalog()
    partial_error_msg = "non-catalog directory already exists"
    with pytest.raises(FileExistsError, match=partial_error_msg):
        test_catalog('create', catalog_dir=dir_path)

def test_create_at_existing_catalog_noforce(tmp_path):
    """
    Test if error is raised when create action is used on an existing catalog
    """
    catalog_path = tmp_path / "test_catalog"
    test_catalog = Catalog()
    test_catalog('create', catalog_dir=catalog_path)

    new_catalog_path = catalog_path
    new_test_catalog = Catalog()

    partial_error_msg = "only possible when using the force argument"
    with pytest.raises(InsufficientArgumentsError, match=partial_error_msg):
        new_test_catalog('create', catalog_dir=new_catalog_path)  

def test_create_at_existing_catalog_force(tmp_path):
    """
    Test if catalog is created when create action is used on an existing catalog,
    together with force flag
    """
    catalog_path = tmp_path / "test_catalog2"
    test_catalog = Catalog()
    test_catalog('create', catalog_dir=catalog_path)

    new_catalog_path = catalog_path
    new_test_catalog = Catalog()
    new_test_catalog('create', catalog_dir=new_catalog_path, force=True)

    assert new_catalog_path.exists()
    assert new_catalog_path.is_dir()

    for p in catalog_paths:
        pth = new_catalog_path / p
        assert pth.exists()