from pathlib import Path
from datalad_catalog.utils import (
    read_json_file,
    md5sum_from_id_version_path,
)
from datalad_catalog.webcatalog import (
    WebCatalog,
    Node,
)
from datalad_catalog.workflow import (
    Workflow,
    super_workflow,
)
from datalad.tests.utils_pytest import (
    assert_equal,
    assert_repo_status,
    skip_if_adjusted_branch,
)
from datalad.api import create, Dataset

from .fixtures import (
    workflow_catalog_path,
    workflow_dataset_path,
)

import json
import pytest
import sys

catalog_workflow = Workflow()
catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/app.js",
    "assets/style.css",
    "artwork",
    "templates",
    "index.html",
    "config.json",
    "README.md",
]


@pytest.mark.skipif(
    sys.platform == "win32", reason="jq does not build on windows"
)
@skip_if_adjusted_branch
def test_workflow_new(test_data, workflow_catalog_path, workflow_dataset_path):
    cat_path = workflow_catalog_path
    super_path = workflow_dataset_path
    ckwa = dict(result_renderer="disabled")
    # Create super and subdataset, save all
    sub_ds = create(super_path / "some_dir" / "subdataset", force=True, **ckwa)
    sub_ds.save(to_git=True, **ckwa)
    super_ds = create(super_path, force=True, **ckwa)
    super_ds.save(to_git=True, **ckwa)
    assert_repo_status(super_ds.path)
    # Test if metadata files exist
    assert (Path(super_ds.path) / ".studyminimeta.yaml").exists()
    assert (Path(sub_ds.path) / "datacite.yml").exists()
    # Create catalog
    cat_path = Path(cat_path)
    cat = WebCatalog(location=cat_path)
    cat.create(config_file=test_data.workflow_config_file, force=True)
    assert cat_path.exists()
    assert cat_path.is_dir()
    for p in catalog_paths:
        pth = cat_path / p
        assert pth.exists()
    # Run workflow
    extractors = [
        "metalad_core",
        "metalad_studyminimeta",
        "datacite_gin",
    ]
    tuple(super_workflow(super_ds, cat, extractors))
    # TODO: test interim workflow outputs, including:
    # - extracted metadata file (amount of lines?)
    # - translated metadata file (amount of lines?)
    assert (Path(super_ds.path) / "extracted_meta.json").exists()
    assert (Path(sub_ds.path) / "extracted_meta.json").exists()
    assert (Path(super_ds.path) / "translated_meta.json").exists()
    assert (Path(sub_ds.path) / "translated_meta.json").exists()

    # Test final workflow outputs
    # - metadata directory
    meta_path = cat_path / "metadata"
    assert meta_path.exists()
    # - "set-super" file
    super_file = cat_path / "metadata" / "super.json"
    assert super_file.exists()
    assert super_file.is_file()
    dataset_details = {
        "super_ds": get_id_and_version(super_ds),
        "sub_ds": get_id_and_version(sub_ds),
    }
    assert_equal(
        json.dumps(read_json_file(super_file), sort_keys=True, indent=2),
        f"""\
{{
  "dataset_id": "{dataset_details["super_ds"][0]}",
  "dataset_version": "{dataset_details["super_ds"][1]}"
}}""",
    )
    # - dataset metadata directory paths
    for ds in dataset_details.values():
        pth = meta_path / str(ds[0]) / str(ds[1])
        assert pth.exists()
    # - Node metadata directories and content: superdataset
    superds_node_path = get_node_path(
        meta_path,
        dataset_details["super_ds"][0],
        dataset_details["super_ds"][1],
    )
    assert superds_node_path.exists()
    generated_meta = read_json_file(superds_node_path)
    correct_meta_path = (
        test_data.data_path / "workflow_generated_meta_super.json"
    )
    correct_meta = read_json_file(correct_meta_path)
    assert_equal(
        list(generated_meta.keys()).sort(), list(correct_meta.keys()).sort()
    )
    keys_to_test = [
        "authors",
        "children",
        "description",
        "keywords",
        "name",
        "publications",
        "type",
        "url",
    ]
    assert_dict_values_equal(generated_meta, correct_meta, keys_to_test)
    # keys_to_test = [
    #     "authors",
    #     "publications",
    # ]
    # assert_dict_values_in_list_equal(generated_meta, correct_meta, keys_to_test)
    assert_super_variable_values_equal(
        generated_meta,
        ["subdatasets", "metadata_sources", "dataset_id", "dataset_version"],
        dataset_details,
    )
    # - Node metadata directories and content: superdataset subdir
    super_subdir_node_path = get_node_path(
        meta_path,
        dataset_details["super_ds"][0],
        dataset_details["super_ds"][1],
        "some_dir",
    )
    assert super_subdir_node_path.exists()
    generated_meta = read_json_file(super_subdir_node_path)
    correct_meta_path = test_data.data_path / "workflow_generated_meta_dir.json"
    correct_meta = read_json_file(correct_meta_path)
    assert_equal(generated_meta.keys(), correct_meta.keys())
    keys_to_test = [
        "path",
        "name",
        "type",
    ]
    assert_dict_values_equal(generated_meta, correct_meta, keys_to_test)
    assert_dir_variable_values_equal(
        generated_meta,
        ["children", "dataset_id", "dataset_version"],
        dataset_details,
    )
    # - Node metadata directories and content: subdataset
    subds_node_path = get_node_path(
        meta_path, dataset_details["sub_ds"][0], dataset_details["sub_ds"][1]
    )
    assert subds_node_path.exists()
    generated_meta = read_json_file(subds_node_path)
    correct_meta_path = test_data.data_path / "workflow_generated_meta_sub.json"
    correct_meta = read_json_file(correct_meta_path)
    assert_equal(
        list(generated_meta.keys()).sort(), list(correct_meta.keys()).sort()
    )
    keys_to_test = [
        "authors",
        "children",
        "description",
        "funding",
        "keywords",
        "publications",
        "license",
        "name",
        "type",
    ]
    assert_dict_values_equal(generated_meta, correct_meta, keys_to_test)
    # keys_to_test = [
    #     "authors",
    #     "publications",
    # ]
    # assert_dict_values_in_list_equal(generated_meta, correct_meta, keys_to_test)
    assert_sub_variable_values_equal(
        generated_meta,
        ["metadata_sources", "dataset_id", "dataset_version"],
        dataset_details,
    )


def get_node_path(root_path, dataset_id, dataset_version, node_path=None):
    _split_dir_length = Node._split_dir_length
    md5_hash = md5sum_from_id_version_path(
        dataset_id,
        dataset_version,
        node_path,
    )
    path_left = md5_hash[:_split_dir_length]
    path_right = md5_hash[_split_dir_length:]
    node_fn = root_path / dataset_id / dataset_version / path_left / path_right
    return node_fn.with_suffix(".json")


def get_id_and_version(dataset: Dataset, var_to_string=False):
    """Helper to get a DataLad dataset's id and version"""
    id = dataset.id
    # sync possible adjusted branch and account for
    # possibility of being on adjusted branch
    dataset.repo.localsync()
    version = dataset.repo.get_hexsha(dataset.repo.get_corresponding_branch())
    if var_to_string:
        return str(id), str(version)
    return id, version


def assert_dict_values_equal(
    dict_to_test: dict,
    dict_correct: dict,
    keys_to_test: list,
):
    """"""

    for key in keys_to_test:
        assert_equal(dict_to_test[key], dict_correct[key])


def assert_dict_values_in_list_equal(
    dict_to_test: dict,
    dict_correct: dict,
    keys_to_test: list,
):
    """"""

    for key in keys_to_test:
        print("---")
        print(key)
        print("---")
        assert_equal(len(dict_to_test[key]), len(dict_correct[key]))
        for val in dict_to_test[key]:
            first_key = list(val.keys())[0]
            print(f"dict_correct[key]: {dict_correct[key]}")
            print(f"dict_to_test[key]: {dict_to_test[key]}")
            print(f"val: {val}")
            print(f"first_key: {first_key}")
            print(f"val[first_key]: {val[first_key]}")
            # print(f"x[first_key]: {x[first_key]}")

            found_obj = [
                x for x in dict_correct[key] if val[first_key] == x[first_key]
            ]
            assert_equal(len(found_obj), 1)


def assert_super_variable_values_equal(
    dict_to_test: dict,
    keys_to_test: list,
    dataset_details: dict,
):
    """"""
    for key in keys_to_test:
        assert key in dict_to_test
    # id and version
    assert_equal(dict_to_test["dataset_id"], dataset_details["super_ds"][0])
    assert_equal(
        dict_to_test["dataset_version"], dataset_details["super_ds"][1]
    )
    # subdatasets
    correct_subds = [
        {
            "dataset_id": f"{dataset_details['sub_ds'][0]}",
            "dataset_path": "some_dir/subdataset",
            "dataset_version": f"{dataset_details['sub_ds'][1]}",
            "dirs_from_path": ["some_dir", "subdataset"],
        }
    ]
    assert_equal(dict_to_test["subdatasets"], correct_subds)
    # extractors_used
    assert_equal(len(dict_to_test["metadata_sources"]["sources"]), 2)
    assert_equal(
        dict_to_test["metadata_sources"]["sources"][0]["source_name"],
        "metalad_core",
    )
    assert_equal(
        dict_to_test["metadata_sources"]["sources"][1]["source_name"],
        "metalad_studyminimeta",
    )


def assert_dir_variable_values_equal(
    dict_to_test: dict,
    keys_to_test: list,
    dataset_details: dict,
):
    """"""
    for key in keys_to_test:
        assert key in dict_to_test
    # id and version
    assert_equal(dict_to_test["dataset_id"], dataset_details["super_ds"][0])
    assert_equal(
        dict_to_test["dataset_version"], dataset_details["super_ds"][1]
    )
    # children
    correct_children = [
        {
            "dataset_id": f"{dataset_details['sub_ds'][0]}",
            "dataset_version": f"{dataset_details['sub_ds'][1]}",
            "name": "subdataset",
            "path": "some_dir/subdataset",
            "type": "dataset",
        }
    ]
    assert_equal(dict_to_test["children"], correct_children)


def assert_sub_variable_values_equal(
    dict_to_test: dict,
    keys_to_test: list,
    dataset_details: dict,
):
    """"""
    for key in keys_to_test:
        assert key in dict_to_test
    # id and version
    assert_equal(dict_to_test["dataset_id"], dataset_details["sub_ds"][0])
    assert_equal(dict_to_test["dataset_version"], dataset_details["sub_ds"][1])
    # extractors_used
    assert_equal(len(dict_to_test["metadata_sources"]["sources"]), 2)
    assert_equal(
        dict_to_test["metadata_sources"]["sources"][0]["source_name"],
        "metalad_core",
    )
    assert_equal(
        dict_to_test["metadata_sources"]["sources"][1]["source_name"],
        "datacite_gin",
    )
