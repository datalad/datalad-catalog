from cgi import test
import hashlib

import pytest

from datalad_catalog import constants as cnst
from datalad_catalog.webcatalog import Node, WebCatalog


@pytest.fixture
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    return WebCatalog(location=catalog_path)


@pytest.fixture
def demo_node_dataset(demo_catalog):
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_type = "dataset"
    test_path = None
    Node._split_dir_length = 3
    return Node(
        catalog=demo_catalog,
        type=test_type,
        dataset_id=test_ds_id,
        dataset_version=test_ds_version,
        node_path=test_path,
    )


@pytest.fixture
def demo_node_directory(demo_catalog):
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_type = "directory"
    dir_path = "dir1/dir2"
    Node._split_dir_length = 3
    return Node(
        catalog=demo_catalog,
        type=test_type,
        dataset_id=test_ds_id,
        dataset_version=test_ds_version,
        node_path=dir_path,
    )


def test_md5hash():
    """
    Test md5 hash of input string
    """
    test_string = "test-string"
    true_output = "661f8009fa8e56a9d0e94a0a644397d7"
    test_hash = hashlib.md5(test_string.encode("utf-8")).hexdigest()
    assert test_hash == true_output


def test_node_location_dataset(
    demo_catalog: WebCatalog, demo_node_dataset: Node
):
    """
    Test location of dataset node as well as interim steps
    """
    demo_node_dataset.parent_catalog = demo_catalog
    long_name = "5df8eb3a-95c5-11ea-b4b9-a0369f287950-dae38cf901995aace0dde5346515a0134f919523"
    assert demo_node_dataset.get_long_name() == long_name
    true_hash = "449268b13a1c869555f6c2f6e66d3923"
    assert demo_node_dataset.md5_hash == true_hash

    metadata_dir = demo_catalog.metadata_path
    location = (
        metadata_dir
        / demo_node_dataset.dataset_id
        / demo_node_dataset.dataset_version
        / "449"
        / "268b13a1c869555f6c2f6e66d3923.json"
    )
    assert demo_node_dataset.get_location() == location


def test_node_location_directory(
    demo_catalog: WebCatalog, demo_node_directory: Node
):
    """
    Test location of directory node as well as interim steps
    """
    demo_node_directory.parent_catalog = demo_catalog
    long_name = "5df8eb3a-95c5-11ea-b4b9-a0369f287950-dae38cf901995aace0dde5346515a0134f919523-dir1/dir2"
    assert demo_node_directory.get_long_name() == long_name
    true_hash = "5eb52c113eb545c1c35647be3a613051"
    assert demo_node_directory.md5_hash == true_hash

    metadata_dir = demo_catalog.metadata_path
    location = (
        metadata_dir
        / demo_node_directory.dataset_id
        / demo_node_directory.dataset_version
        / "5eb"
        / "52c113eb545c1c35647be3a613051.json"
    )
    assert demo_node_directory.get_location() == location


def test_add_child_new(demo_node_directory: Node):
    """
    Test if the first child is correctly added to Node instance
    """
    test_child_file = {cnst.TYPE: cnst.TYPE_FILE, cnst.NAME: "temp_file"}
    assert not demo_node_directory.children
    demo_node_directory.add_child(test_child_file)
    assert len(demo_node_directory.children) == 1
    assert (
        demo_node_directory.children[0][cnst.TYPE] == test_child_file[cnst.TYPE]
    )
    assert (
        demo_node_directory.children[0][cnst.NAME] == test_child_file[cnst.NAME]
    )


def test_add_child_existing(demo_node_directory: Node):
    """
    Test behaviour when existing child is added again to Node instance
    """
    test_child_file = {cnst.TYPE: cnst.TYPE_FILE, cnst.NAME: "temp_file"}
    demo_node_directory.children.append(test_child_file)
    demo_node_directory.add_child(test_child_file)
    assert len(demo_node_directory.children) == 1
    assert (
        demo_node_directory.children[0][cnst.TYPE] == test_child_file[cnst.TYPE]
    )
    assert (
        demo_node_directory.children[0][cnst.NAME] == test_child_file[cnst.NAME]
    )
