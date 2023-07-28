import pytest
from pathlib import Path

from datalad_catalog import constants as cnst
from datalad_catalog.webcatalog import (
    Node,
)

tests_path = Path(__file__).resolve().parent
package_path = Path(__file__).resolve().parent.parent
data_path = tests_path / "data"
default_config_path = package_path / "config" / "config.json"
demo_config_path_catalog = data_path / "test_config_file_catalog.json"
demo_config_path_dataset = data_path / "test_config_file_dataset.json"
metadata_path1 = data_path / "catalog_metadata_dataset.jsonl"
metadata_path2 = data_path / "catalog_metadata_dataset2.jsonl"


demo_config = {
    "property_sources": {
        "dataset": {
            "dataset_id": {"rule": "single", "source": "metalad_core"},
            "keywords": {"rule": "merge", "source": "any"},
            "authors": {"rule": "merge", "source": ["metalad_studyminimeta"]},
            "description": {
                "rule": "priority",
                "source": [
                    "metalad_studyminimeta",
                    "datacite_gin",
                    "bids_dataset",
                ],
            },
            "doi": {"rule": "xxxx", "source": "yyy"},
            "license": {},
            "funding": {"source": "any"},
            "subdatasets": {"source": "metalad_core"},
            "dataset_version": {
                "rule": "single",
            },
        }
    }
}

# Some handling of incorrect config specification:
# - "rule" can be one of: single / merge / priority / None / empty string
# - "source" can be: "any" / a list / empty list / empty string


# If config_rule specified without config_source:
# for merge, allow new source to be merged
# for single / priority / None, ignore new source

# If config_source specified without config_rule,
# set config_rule to None (i.e. first-come-first-served)

# If config_source is "any" it implies the current source is allowed


# If config_rule is None or unspecified or something random,
# ==> first-come-first-served


@pytest.fixture
def demo_node_dataset(demo_catalog):
    test_ds_id = "5df8eb3a-95c5-11ea-b4b9-a0369f287950"
    test_ds_version = "dae38cf901995aace0dde5346515a0134f919523"
    test_type = "dataset"
    test_path = None
    Node._split_dir_length = 3
    node_instance = Node(
        catalog=demo_catalog,
        type=test_type,
        dataset_id=test_ds_id,
        dataset_version=test_ds_version,
        node_path=test_path,
    )
    node_instance.config = demo_config
    node_instance.config_source = "dataset"
    return node_instance


@pytest.fixture
def demo_metadata():
    metadata_core = {
        "name": "Core Catalog Name",
        "dataset_id": "core_id",
        "keywords": [
            "keyword1",
            "keyword2",
            "keyword3",
        ],
        "authors": [
            {"firstname": "John", "lastname": "Doe"},
            {"firstname": "Jane", "lastname": "Bo"},
        ],
        "description": "",
        "subdatasets": [
            {
                "dataset_id": "7fcd8812-d0fe-11e7-8db2-a0369f7c647e",
                "dataset_version": "2ccaa115543c21e6658950d1cb8cc3038f14272f",
                "dataset_path": "derivative/aggregate_fmri_timeseries",
                "dirs_from_path": ["derivative", "aggregate_fmri_timeseries"],
            },
            {
                "dataset_id": "c8ec2919-493b-4af5-9271-cbe9ebd08c43",
                "dataset_version": "74cd7ec0538448b05fb4d5f91119b279c5e9ab04",
                "dataset_path": "derivative/aligned_mri",
                "dirs_from_path": ["derivative", "aligned_mri"],
            },
        ],
        cnst.METADATA_SOURCES: {
            cnst.KEY_SOURCE_MAP: {},
            cnst.SOURCES: [{cnst.SOURCE_NAME: "metalad_core"}],
        },
    }
    metadata_studyminimeta = {
        "name": "Minimeta Catalog Name",
        "dataset_id": "minimeta_id",
        "keywords": [
            "keyword3",
            "keyword4",
            "keyword5",
        ],
        "description": "Minimeta description",
        "doi": "https://doi.org/minimeta",
        "authors": [
            {"firstname": "mini", "lastname": "Doe"},
            {"firstname": "micky", "lastname": "Flo"},
        ],
        "license": {},
        "funding": {},
        "subdatasets": [],
        "dataset_version": "",
        cnst.METADATA_SOURCES: {
            cnst.KEY_SOURCE_MAP: {},
            cnst.SOURCES: [{cnst.SOURCE_NAME: "metalad_studyminimeta"}],
        },
    }
    metadata_bids = {
        "name": "Bids Catalog Name",
        "dataset_id": "bids_id",
        "keywords": [
            "bids_kw1",
            "bids_kw2",
            "bids_kw3",
        ],
        "description": "BIDS description",
        "doi": "https://doi.org/bids",
        "authors": [
            {"firstname": "Bidsy", "lastname": "Doe"},
            {"firstname": "Tootsy", "lastname": "Flo"},
        ],
        cnst.METADATA_SOURCES: {
            cnst.KEY_SOURCE_MAP: {},
            cnst.SOURCES: [{cnst.SOURCE_NAME: "bids_dataset"}],
        },
    }
    metadata_datacitegin = {
        "description": "GIN description",
        cnst.METADATA_SOURCES: {
            cnst.KEY_SOURCE_MAP: {},
            cnst.SOURCES: [{cnst.SOURCE_NAME: "datacite_gin"}],
        },
    }

    obj = {
        "metalad_core": metadata_core,
        "metalad_studyminimeta": metadata_studyminimeta,
        "bids_dataset": metadata_bids,
        "datacite_gin": metadata_datacitegin,
    }
    return obj


def test_rules_and_sources(demo_node_dataset: Node, demo_metadata: dict):
    """"""

    assert demo_node_dataset.parent_catalog is not None
    # node already has id, version, and type from instantiation
    # other attributes corresponding to those that be added are None
    orig_version = demo_node_dataset.dataset_version
    bids_attributes = demo_metadata["bids_dataset"]
    minimeta_attributes = demo_metadata["metalad_studyminimeta"]
    core_attributes = demo_metadata["metalad_core"]
    datacite_attributes = demo_metadata["datacite_gin"]

    # TO TEST:
    # id: single; core
    # authors: merge; studyminimeta
    # keywords: merge; any
    # description: priority; metalad_studyminimeta, datacite_gin, bids_dataset
    # doi: incorrect rule and incorrect source
    # license: no rule; no source
    # funding: no rule; any
    # subdatasets: no rule; core
    # version: single; no source

    # 1) add core attributes
    demo_node_dataset.add_attributes(core_attributes)
    assert (
        demo_node_dataset.dataset_id == core_attributes["dataset_id"]
    )  # test: single source
    assert (
        demo_node_dataset.authors is None
    )  # test: current source not in merge list
    assert (
        demo_node_dataset.keywords == core_attributes["keywords"]
    )  # test: merge any
    assert not hasattr(
        demo_node_dataset, "description"
    )  # test: empty/missing value is skipped
    assert not hasattr(
        demo_node_dataset, "doi"
    )  # test: empty/missing value is skipped
    assert not hasattr(
        demo_node_dataset, "license"
    )  # test: empty/missing value is skipped
    assert not hasattr(
        demo_node_dataset, "funding"
    )  # test: empty/missing value is skipped
    assert (
        demo_node_dataset.subdatasets == core_attributes["subdatasets"]
    )  # test: no rule, core, first come first served
    assert demo_node_dataset.name == None  # test: single source not current
    assert (
        demo_node_dataset.dataset_version == orig_version
    )  # test: single, no source, ignore incoming
    assert (
        "metalad_core"
        in demo_node_dataset.metadata_sources["key_source_map"]["dataset_id"]
    )
    assert (
        "metalad_core"
        in demo_node_dataset.metadata_sources["key_source_map"]["keywords"]
    )
    assert (
        "metalad_core"
        in demo_node_dataset.metadata_sources["key_source_map"]["subdatasets"]
    )
    assert {
        "source_name": "metalad_core"
    } in demo_node_dataset.metadata_sources["sources"]

    # 2) add BIDS attributes
    demo_node_dataset.add_attributes(bids_attributes)
    assert (
        demo_node_dataset.dataset_id == core_attributes["dataset_id"]
    )  # test: current source not single source
    assert (
        demo_node_dataset.authors is None
    )  # test: current source not in merge list
    assert (
        demo_node_dataset.keywords.sort()
        == list(
            set(core_attributes["keywords"] + bids_attributes["keywords"])
        ).sort()
    )  # test: merge any
    assert (
        demo_node_dataset.description == bids_attributes["description"]
    )  # test: current source low in priority list, and first
    assert (
        demo_node_dataset.doi == bids_attributes["doi"]
    )  # test: incorrect rule, first come first served
    assert not hasattr(
        demo_node_dataset, "license"
    )  # test: empty/missing value is skipped
    assert not hasattr(
        demo_node_dataset, "funding"
    )  # test: empty/missing value is skipped
    assert (
        demo_node_dataset.subdatasets == core_attributes["subdatasets"]
    )  # test: no rule, core, first come first served already applied
    assert demo_node_dataset.name == None  # test: single source, not current
    assert (
        demo_node_dataset.dataset_version == orig_version
    )  # test: single, no source, ignore incoming
    assert (
        "bids_dataset"
        in demo_node_dataset.metadata_sources["key_source_map"]["description"]
    )
    assert (
        "metalad_core"
        in demo_node_dataset.metadata_sources["key_source_map"]["keywords"]
    )
    assert (
        "bids_dataset"
        in demo_node_dataset.metadata_sources["key_source_map"]["keywords"]
    )
    assert (
        "bids_dataset"
        in demo_node_dataset.metadata_sources["key_source_map"]["description"]
    )
    assert (
        "bids_dataset"
        in demo_node_dataset.metadata_sources["key_source_map"]["doi"]
    )
    assert {
        "source_name": "metalad_core"
    } in demo_node_dataset.metadata_sources["sources"]
    assert {
        "source_name": "bids_dataset"
    } in demo_node_dataset.metadata_sources["sources"]

    # 3) add studyminimeta attributes
    demo_node_dataset.add_attributes(minimeta_attributes)
    assert (
        demo_node_dataset.dataset_id == core_attributes["dataset_id"]
    )  # test: current source not single source
    assert (
        demo_node_dataset.authors == minimeta_attributes["authors"]
    )  # test: current source in merge list
    assert (
        demo_node_dataset.keywords.sort()
        == list(
            set(
                core_attributes["keywords"]
                + bids_attributes["keywords"]
                + minimeta_attributes["keywords"]
            )
        ).sort()
    )  # test: merge any
    assert (
        demo_node_dataset.description == minimeta_attributes["description"]
    )  # test: current source higher in priority list, replacing previous
    assert (
        demo_node_dataset.doi == bids_attributes["doi"]
    )  # test: incorrect rule, first come first served
    assert not hasattr(
        demo_node_dataset, "license"
    )  # test: empty/missing value is skipped
    assert not hasattr(
        demo_node_dataset, "funding"
    )  # test: empty/missing value is skipped
    assert (
        demo_node_dataset.subdatasets == core_attributes["subdatasets"]
    )  # test: no rule, core, first come first served already applied
    assert (
        demo_node_dataset.name == minimeta_attributes["name"]
    )  # test: single source, now incoming
    assert (
        demo_node_dataset.dataset_version == orig_version
    )  # test: single, no source, ignore incoming
    assert (
        "metalad_studyminimeta"
        in demo_node_dataset.metadata_sources["key_source_map"]["authors"]
    )
    assert (
        "metalad_studyminimeta"
        in demo_node_dataset.metadata_sources["key_source_map"]["description"]
    )
    assert (
        "metalad_core"
        in demo_node_dataset.metadata_sources["key_source_map"]["keywords"]
    )
    assert (
        "bids_dataset"
        in demo_node_dataset.metadata_sources["key_source_map"]["keywords"]
    )
    assert (
        "metalad_studyminimeta"
        in demo_node_dataset.metadata_sources["key_source_map"]["keywords"]
    )
    assert (
        "metalad_studyminimeta"
        in demo_node_dataset.metadata_sources["key_source_map"]["name"]
    )
    assert {
        "source_name": "metalad_core"
    } in demo_node_dataset.metadata_sources["sources"]
    assert {
        "source_name": "bids_dataset"
    } in demo_node_dataset.metadata_sources["sources"]
    assert {
        "source_name": "metalad_studyminimeta"
    } in demo_node_dataset.metadata_sources["sources"]

    # 4) add datacite attributes
    demo_node_dataset.add_attributes(datacite_attributes)
    assert (
        demo_node_dataset.description == minimeta_attributes["description"]
    )  # test: current source lower in priority list, do nothing
    assert {
        "source_name": "metalad_core"
    } in demo_node_dataset.metadata_sources["sources"]
    assert {
        "source_name": "bids_dataset"
    } in demo_node_dataset.metadata_sources["sources"]
    assert {
        "source_name": "metalad_studyminimeta"
    } in demo_node_dataset.metadata_sources["sources"]
    assert {
        "source_name": "datacite_gin"
    } in demo_node_dataset.metadata_sources["sources"]
