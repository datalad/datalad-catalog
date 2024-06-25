from datalad_catalog.schema_utils import (
    get_schema_item,
    get_metadata_item,
)


ds = {
    "type": "dataset",
    "dataset_id": "",
    "dataset_version": "",
    "name": "",
    "alias": "",
    "short_name": "",
    "description": "",
    "doi": "",
    "url": "",
    "download_url": "",
    "homepage_url": "",
    "license": {"name": "", "url": ""},
    "authors": [
        {
            "givenName": "",
            "familyName": "",
            "name": "",
            "email": "",
            "honorificSuffix": "",
            "identifiers": [{"type": "", "identifier": ""}],
        }
    ],
    "access_request_contact": {
        "givenName": "",
        "familyName": "",
        "name": "",
        "email": "",
        "honorificSuffix": "",
        "identifiers": [{"type": "", "identifier": ""}],
    },
    "access_request_url": "",
    "keywords": [""],
    "funding": [{"name": "", "identifier": "", "description": ""}],
    "publications": [
        {
            "type": "",
            "title": "",
            "doi": "",
            "datePublished": "",
            "publicationOutlet": "",
            "authors": [
                {
                    "givenName": "",
                    "familyName": "",
                    "name": "",
                    "email": "",
                    "honorificSuffix": "",
                    "identifiers": [{"type": "", "identifier": ""}],
                }
            ],
        }
    ],
    "subdatasets": [
        {"dataset_id": "", "dataset_version": "", "dataset_path": ""}
    ],
    "metadata_sources": {
        "key_source_map": {},
        "sources": [
            {
                "source_name": "",
                "source_version": "",
                "source_parameter": {},
                "source_time": 0.0,
                "agent_name": "",
                "agent_email": "",
            }
        ],
    },
    "additional_display": [{"name": "", "content": {}, "icon": ""}],
    "top_display": [{"name": "", "value": ""}],
    "notebooks": [
        {
            "git_repo_url": "",
            "notebook_path": "",
        },
    ],
}

fl = {
    "type": "file",
    "dataset_id": "",
    "dataset_version": "",
    "path": "",
    "contentbytesize": 0.0,
    "url": "",
    "metadata_sources": {
        "key_source_map": {},
        "sources": [
            {
                "source_name": "",
                "source_version": "",
                "source_parameter": {},
                "source_time": 0.0,
                "agent_name": "",
                "agent_email": "",
            }
        ],
    },
    "additional_display": [{"name": "", "content": {}}],
}


def test_get_dicts():
    tp = "dataset"
    assert get_schema_item(item_type=tp) == ds
    tp = "file"
    assert get_schema_item(item_type=tp) == fl


def test_get_meta_items():
    """"""
    get_metadata_item(
        item_type="file",
        dataset_id="my_ds_id",
        dataset_version="my_ds_version",
        source_name="wackystuff",
        source_version="wack.point.zero",
        path="testy/festy/bob.txt",
        required_only=True,
    )
    get_metadata_item(
        item_type="dataset",
        dataset_id="my_ds_id",
        dataset_version="my_ds_version",
        source_name="wackystuff",
        source_version="wack.point.zero",
        path=None,
        required_only=True,
    )


def test_exclude_keys():
    item = get_metadata_item(
        item_type="file",
        dataset_id="my_ds_id",
        dataset_version="my_ds_version",
        source_name="wackystuff",
        source_version="wack.point.zero",
        exclude_keys=["path"],
    )
