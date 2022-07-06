import hashlib

import pytest

from datalad_catalog import constants as cnst
from datalad_catalog.webcatalog import (
    Node,
    WebCatalog,
    getNode,
)


@pytest.fixture
def demo_node_dataset():
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_type = "dataset"
    Node._split_dir_length = 3
    return Node(
        type=test_type, dataset_id=test_ds_id, dataset_version=test_ds_version
    )


@pytest.fixture
def demo_node_directory():
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_type = "directory"
    dir_path = "dir1/dir2"
    Node._split_dir_length = 3
    return Node(
        type=test_type,
        dataset_id=test_ds_id,
        dataset_version=test_ds_version,
        node_path=dir_path,
    )


@pytest.fixture
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    return WebCatalog(location=catalog_path)


def test_node_instances_equal():
    """
    Assert that two instances with identical variables, one created via class
    instantiation and one created via getNode method, are the same object
    """
    node_instance_1 = Node(
        type="dataset", dataset_id="123", dataset_version="v1"
    )
    node_instance_2 = getNode(
        type="dataset", dataset_id="123", dataset_version="v1"
    )
    assert node_instance_1 == node_instance_2


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


def test_add_attributes(demo_catalog: WebCatalog, demo_node_directory: Node):
    """
    Test if attributes are correctly added to Node instance
    """
    test_key = "url"
    test_value = "value1"
    test_attributes = {test_key: test_value}
    demo_node_directory.parent_catalog = demo_catalog
    demo_node_directory.add_attribrutes(test_attributes, demo_catalog)
    assert hasattr(demo_node_directory, test_key)
    assert demo_node_directory.url == test_value


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


def test_add_extractor_new(demo_node_directory: Node):
    """
    Test if the first extractor is correctly added to Node instance
    """
    test_extractor = {
        cnst.EXTRACTOR_NAME: "metalad_core",
        cnst.EXTRACTOR_VERSION: "1",
        cnst.EXTRACTION_PARAMETER: {},
        cnst.EXTRACTION_TIME: "1234567890",
    }
    assert not hasattr(demo_node_directory, "extractors_used")
    demo_node_directory.add_extractor(test_extractor)
    assert len(demo_node_directory.extractors_used) == 1
    for key in test_extractor:
        assert (
            demo_node_directory.extractors_used[0][key] == test_extractor[key]
        )


def test_add_extractor_existing(demo_node_directory: Node):
    """
    Test behaviour when existing extractor is added again to Node instance
    """
    test_extractor = {
        cnst.EXTRACTOR_NAME: "metalad_core",
        cnst.EXTRACTOR_VERSION: "1",
        cnst.EXTRACTION_PARAMETER: {},
        cnst.EXTRACTION_TIME: "1234567890",
    }
    demo_node_directory.extractors_used = []
    demo_node_directory.add_extractor(test_extractor)
    assert len(demo_node_directory.extractors_used) == 1
    for key in test_extractor:
        assert (
            demo_node_directory.extractors_used[0][key] == test_extractor[key]
        )
