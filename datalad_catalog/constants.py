# A module to store all constants
from pathlib import Path

# Paths
package_path = Path(__file__).resolve().parent
catalog_path = package_path / "catalog"
schema_dir = catalog_path / "schema"
tests_path = package_path / "tests"
default_config_dir = package_path / "config"

# Keys
ATGRAPH = "@graph"
ATID = "@id"
ATLIST = "@list"
ATTYPE = "@type"
AUTHOR = "author"
AUTHORS = "authors"
CATALOG = "catalog"
CATALOG_NAME = "catalog_name"
CHILDREN = "children"
CONTENT = "content"
CONTENTBYTESIZE = "contentbytesize"
CREATIVEWORK = "CreativeWork"
DESCRIPTION = "description"
DOI = "doi"
DOLLARID = "$id"
DIRECTORY = "directory"
DATASET_ID = "dataset_id"
DATASET_PATH = "dataset_path"
DATASET_VERSION = "dataset_version"
DIRSFROMPATH = "dirs_from_path"
DISTRIBUTION = "distribution"
EXTRACTED_METADATA = "extracted_metadata"
EXTRACTION_PARAMETER = "extraction_parameter"
EXTRACTION_TIME = "extraction_time"
EXTRACTOR_CORE = "metalad_core"
EXTRACTOR_CORE_DATASET = (
    "metalad_core_dataset"  # older version; core is newer version
)
EXTRACTOR_NAME = "extractor_name"
EXTRACTOR_STUDYMINIMETA = "metalad_studyminimeta"
EXTRACTOR_VERSION = "extractor_version"
EXTRACTORS = "extractors"
EXTRACTORS_USED = "extractors_used"
HASPART = "hasPart"
IDENTIFIER = "identifier"
KEY_SOURCE_MAP = "key_source_map"
LOGO_PATH = "logo_path"
METADATA_SOURCES = "metadata_sources"
NAME = "name"
ORIGIN = "origin"
PATH = "path"
PERSONLIST = "#personList"
PROPERTY_SOURCES = "property_sources"
PUBLICATION = "publication"
PUBLICATIONS = "publications"
PUBLICATIONLIST = "#publicationList"
SAMEAS = "sameAs"
SOURCE = "source"
SOURCES = "sources"
SOURCE_NAME = "source_name"
SOURCE_VERSION = "source_version"
SOURCE_PARAMETER = "source_parameter"
SOURCE_TIME = "source_time"
STRIPDATALAD = "datalad:"
STUDY = "study"
SUBDATASETS = "subdatasets"
TYPE = "type"
TYPE_DATASET = "dataset"
TYPE_DIRECTORY = "directory"
TYPE_FILE = "file"
URL = "url"
VERSION = "version"

# Schema
CATALOG_SCHEMA_IDS = {
    CATALOG: "https://datalad.org/catalog.schema.json",
    TYPE_DATASET: "https://datalad.org/catalog.dataset.schema.json",
    TYPE_FILE: "https://datalad.org/catalog.file.schema.json",
    AUTHORS: "https://datalad.org/catalog.authors.schema.json",
    METADATA_SOURCES: "https://datalad.org/catalog.metadata_sources.schema.json",
}
