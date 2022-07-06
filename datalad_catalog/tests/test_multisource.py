import pytest

from datalad_catalog import constants as cnst
from datalad_catalog.webcatalog import (
    Node,
    WebCatalog,
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
def demo_catalog(tmp_path):
    catalog_path = tmp_path / "test_catalog"
    return WebCatalog(location=catalog_path)


@pytest.fixture
def demo_metadata():
    metadata_item_important = {
        "name": "Important Catalog Name",
        "keywords": [
            "keyword1",
            "keyword2",
            "keyword3",
        ],
        "authors": [
            {"firstname": "John", "lastname": "Doe"},
            {"firstname": "Jane", "lastname": "Bo"},
        ],
        cnst.EXTRACTORS_USED: [
            {cnst.EXTRACTOR_NAME: "metadata_source_important"}
        ],
    }
    metadata_item_random = {
        "name": "Random Catalog Name",
        "keywords": [
            "keyword3",
            "keyword4",
            "keyword5",
        ],
        "authors": [
            {"firstname": "John", "lastname": "Doe"},
            {"firstname": "Jenny", "lastname": "Flo"},
        ],
        cnst.EXTRACTORS_USED: [{cnst.EXTRACTOR_NAME: "metadata_source_random"}],
    }
    obj = {
        "metadata_source_important": metadata_item_important,
        "metadata_source_random": metadata_item_random,
    }
    return obj


def test_important_source(
    demo_catalog: WebCatalog, demo_node_dataset: Node, demo_metadata: dict
):
    """
    When the metadata source is specified in config as a single name (e.g.
    "metalad_core"), this source should receive priority and replace existing
    values.
    """
    demo_node_dataset.parent_catalog = demo_catalog
    metadata_source = "metadata_source_important"
    demo_catalog.config = {
        "property_source": {
            "dataset": {
                "name": metadata_source,
                "keywords": metadata_source,
                "authors": metadata_source,
            }
        }
    }
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    for key in demo_metadata[metadata_source].keys():
        if key == cnst.EXTRACTORS_USED:
            continue
        assert hasattr(demo_node_dataset, key)
        assert (
            getattr(demo_node_dataset, key)
            == demo_metadata[metadata_source][key]
        )

    metadata_source = "metadata_source_random"
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    for key in demo_metadata[metadata_source].keys():
        if key == cnst.EXTRACTORS_USED:
            continue
        assert hasattr(demo_node_dataset, key)
        assert (
            getattr(demo_node_dataset, key)
            == demo_metadata["metadata_source_important"][key]
        )
    assert hasattr(demo_node_dataset, cnst.EXTRACTORS_USED)
    assert getattr(demo_node_dataset, cnst.EXTRACTORS_USED) == [
        {cnst.EXTRACTOR_NAME: "metadata_source_important"},
        {cnst.EXTRACTOR_NAME: "metadata_source_random"},
    ]


def test_merge_sources(
    demo_catalog: WebCatalog, demo_node_dataset: Node, demo_metadata: dict
):
    """
    When the metadata source is specified in config as "merge", the incoming
    metadata should be merged with any existing metadata, as a list.
    """
    demo_node_dataset.parent_catalog = demo_catalog
    metadata_source = "metadata_source_important"
    demo_catalog.config = {
        "property_source": {
            "dataset": {
                "name": metadata_source,
                "keywords": "merge",
                "authors": "merge",
            }
        }
    }
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    for key in demo_metadata[metadata_source].keys():
        if key == cnst.EXTRACTORS_USED:
            continue
        assert hasattr(demo_node_dataset, key)
        assert (
            getattr(demo_node_dataset, key)
            == demo_metadata[metadata_source][key]
        )

    metadata_source = "metadata_source_random"
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )

    key = "keywords"
    assert hasattr(demo_node_dataset, key)
    assert getattr(demo_node_dataset, key) == list(
        set(
            demo_metadata["metadata_source_important"][key]
            + demo_metadata["metadata_source_random"][key]
        )
    )

    key = "authors"
    assert hasattr(demo_node_dataset, key)
    assert getattr(demo_node_dataset, key) == [
        {"firstname": "John", "lastname": "Doe"},
        {"firstname": "Jane", "lastname": "Bo"},
        {"firstname": "Jenny", "lastname": "Flo"},
    ]

    assert hasattr(demo_node_dataset, cnst.EXTRACTORS_USED)
    assert getattr(demo_node_dataset, cnst.EXTRACTORS_USED) == [
        {cnst.EXTRACTOR_NAME: "metadata_source_important"},
        {cnst.EXTRACTOR_NAME: "metadata_source_random"},
    ]


def test_multiple_sources(
    demo_catalog: WebCatalog, demo_node_dataset: Node, demo_metadata: dict
):
    """
    When the metadata source is specified in config as a list (e.g.
    ["metalad_studyminimeta", "datacite_gin"]), the output metadata
    for the applicatble attribute data should be a list of dicts of the form:
        [
            {
                "source": data_source_1,
                "content": value_1
            },
            {
                "source": data_source_2,
                "content": value_2
            }
        ]
    """
    demo_node_dataset.parent_catalog = demo_catalog
    metadata_source = "metadata_source_important"
    demo_catalog.config = {
        "property_source": {
            "dataset": {
                "name": ["metadata_source_important", "metadata_source_random"],
                "keywords": [
                    "metadata_source_important",
                    "metadata_source_random",
                ],
                "authors": [
                    "metadata_source_important",
                    "metadata_source_random",
                ],
            }
        }
    }
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    key = "name"
    assert hasattr(demo_node_dataset, key)
    assert getattr(demo_node_dataset, key) == [
        {
            "source": metadata_source,
            "content": demo_metadata[metadata_source][key],
        }
    ]
    metadata_source = "metadata_source_random"
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    for key in ["name", "keywords", "authors"]:
        assert hasattr(demo_node_dataset, key)
        assert getattr(demo_node_dataset, key) == [
            {
                "source": "metadata_source_important",
                "content": demo_metadata["metadata_source_important"][key],
            },
            {
                "source": metadata_source,
                "content": demo_metadata[metadata_source][key],
            },
        ]


def test_no_source_config(
    demo_catalog: WebCatalog, demo_node_dataset: Node, demo_metadata: dict
):
    """
    When the metadata source is not specified in the config, first value is
    written as instance variable. Subsequent values should not replace the
    existing value.
    """
    demo_node_dataset.parent_catalog = demo_catalog
    metadata_source = "metadata_source_important"
    demo_catalog.config = {"property_source": {"dataset": {}}}
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    for key in demo_metadata[metadata_source].keys():
        if key == cnst.EXTRACTORS_USED:
            continue
        assert hasattr(demo_node_dataset, key)
        assert (
            getattr(demo_node_dataset, key)
            == demo_metadata[metadata_source][key]
        )

    metadata_source = "metadata_source_random"
    demo_node_dataset.add_attribrutes(
        demo_metadata[metadata_source], demo_catalog
    )
    for key in demo_metadata[metadata_source].keys():
        if key == cnst.EXTRACTORS_USED:
            continue
        assert hasattr(demo_node_dataset, key)
        assert (
            getattr(demo_node_dataset, key)
            == demo_metadata["metadata_source_important"][key]
        )

    assert hasattr(demo_node_dataset, cnst.EXTRACTORS_USED)
    assert getattr(demo_node_dataset, cnst.EXTRACTORS_USED) == [
        {cnst.EXTRACTOR_NAME: "metadata_source_important"},
        {cnst.EXTRACTOR_NAME: "metadata_source_random"},
    ]
