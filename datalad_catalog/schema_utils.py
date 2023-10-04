import datalad_catalog.constants as cnst
from datalad_catalog.validate import get_schema_store
from datalad_catalog.utils import get_gitconfig
from datetime import datetime


SCHEMA_TYPES = [
    "dataset",
    "file",
    "authors",
    "metadata_sources",
]


def get_schema_item(
    catalog=None,
    item_type: str = "dataset",
    required_only: bool = False,
):
    """Returns an empty metadata item of the specified type"""
    # only existing schema items are allowed
    assert item_type in SCHEMA_TYPES
    # get the full store for catalog (if provided) or package
    store = get_schema_store(catalog)
    # get the desired schema
    schema = store[cnst.CATALOG_SCHEMA_IDS[item_type]]
    return _schema_process_property(item_type, schema, store, required_only)


def _schema_process_property(
    item_type: str, item: dict, store: dict, required_only: bool
):
    # First, process $ref
    if cnst.DOLLARREF in item:
        ref = item[cnst.DOLLARREF]
        if ref not in store:
            return None
        else:
            item = store[ref]
    # process type null
    if cnst.TYPE not in item or not item[cnst.TYPE]:
        return None
    # grab type specifics
    tp = item[cnst.TYPE]
    rq = item.get(cnst.REQUIRED, [])
    # process multiple types (prefer easiest elements)
    if tp and isinstance(tp, list):
        if "string" in tp:
            tp = "string"
        elif "number" in tp:
            tp = "number"
        else:
            tp = tp[0]
    # process type object
    if tp == "object":
        if cnst.PROPERTIES not in item:
            return {}
        new_item = {}
        for key, value in item[cnst.PROPERTIES].items():
            if required_only and key not in rq:
                continue
            # for files and datasets, set correct 'type'
            if key == cnst.TYPE:
                new_item[key] = item_type
            else:
                new_item[key] = _schema_process_property(
                    item_type, value, store, required_only
                )
        return new_item
    # type string
    if tp == "string":
        return ""
    # type array
    if tp == "array":
        if cnst.ITEMS in item:
            return [
                _schema_process_property(
                    "", item[cnst.ITEMS], store, required_only
                )
            ]
        else:
            return []
    # type number
    if tp == "number":
        return 0.0
    # if all else fails
    return None


def get_metadata_sources(name: str, version: str, required_only: bool = False):
    """Create metadata_sources dict required by catalog schema"""
    metadata_sources = get_schema_item(
        item_type="metadata_sources",
        required_only=required_only,
    )
    metadata_sources[cnst.SOURCES][0][cnst.SOURCE_NAME] = name
    metadata_sources[cnst.SOURCES][0][cnst.SOURCE_VERSION] = version
    if not required_only:
        metadata_sources[cnst.SOURCES][0][
            cnst.SOURCE_TIME
        ] = datetime.now().timestamp()
        metadata_sources[cnst.SOURCES][0]["agent_email"] = get_gitconfig(
            "user.email"
        )
        metadata_sources[cnst.SOURCES][0]["agent_name"] = get_gitconfig(
            "user.name"
        )

    return metadata_sources


def get_metadata_item(
    item_type,
    dataset_id: str,
    dataset_version: str,
    source_name: str,
    source_version: str,
    path=None,
    required_only: bool = True,
):
    assert item_type in ("dataset", "file")
    if item_type == "file" and not path:
        raise ValueError("Path is a required field for item type 'file'")
    meta_item = get_schema_item(
        item_type=item_type,
        required_only=required_only,
    )
    meta_item[cnst.DATASET_ID] = dataset_id
    meta_item[cnst.DATASET_VERSION] = dataset_version
    if item_type == "file":
        meta_item[cnst.PATH] = path
    meta_item[cnst.METADATA_SOURCES] = get_metadata_sources(
        source_name,
        source_version,
    )
    return meta_item
