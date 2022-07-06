import pytest

from datalad_catalog.webcatalog import (
    Node,
    WebCatalog,
)


@pytest.fixture
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    return WebCatalog(location=catalog_path)


@pytest.fixture
def demo_node_dataset():
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_type = "dataset"
    Node._split_dir_length = 3
    return Node(
        type=test_type, dataset_id=test_ds_id, dataset_version=test_ds_version
    )


test_list = [
    {"source": "metalad_studyminimeta", "content": ["mini1", "mini2", "mini3"]},
    {"source": "datacite_gin", "content": ["gin1", "gin2"]},
]
test_object_true = {"source": "datacite_gin", "content": ["gin1", "gin2"]}
test_object_half_false = {"source": "metalad_studyminimeta", "content": []}
test_object_false = {"source": "wrong_thing", "content": []}
