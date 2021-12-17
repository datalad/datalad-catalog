import sys
import json
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import hashlib
from . import constants as cnst
from .webcatalog import Node


class Translator(object):
    """
    Parse a single metadata item from the list input to `datalad_catalog`,
    using a different parser based on the `extractor_name` field of the item.
    Uses subclasses for extractor-specific parsing.
    """

    # Get package-related paths/content
    package_path = Path(__file__).resolve().parent
    templates_path = package_path / 'templates'

    def __init__(self, meta_object, node_object) -> None:
        # Dictionary to select relevant class based on the extractor used to
        # generate the incoming metadata object
        self.translatorSelector = {
            cnst.EXTRACTOR_CORE: CoreTranslator(),
            cnst.EXTRACTOR_CORE_DATASET: CoreDatasetTranslator,
            cnst.EXTRACTOR_STUDYMINIMETA: StudyminimetaTranslator,
        }
        try:
            # TODO: 
            newTranslator = self.translatorSelector.get(meta_object[cnst.EXTRACTOR_NAME])(meta_object, node_object)
        except:
            # TODO: handle unrecognised extractors
            pass

    def __cal__():
        """Call single instance when needed"""

    def load_schema(self, meta_object, node_object):

        schema = load_json_file(self.schema_file)
        # Copy source to destination values, per key
        for key in schema:
            if schema[key] in meta_object:

                node_object[key] = meta_object[schema[key]]
        return node_object
    


class CoreTranslator(Translator):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    """

    def __init__(self, meta_object, node_object) -> None:
        """"""
        # Assign schema file for dataset/file
        self.type = meta_object[cnst.TYPE]
        if meta_object[cnst.TYPE] == cnst.TYPE_DATASET:
            self.schema_file = self.package_path / cnst.SCHEMA_CORE_FOR_DATASET
        else:
            self.schema_file = self.package_path / cnst.SCHEMA_CORE_FOR_FILE
        # Load basic fields for dataset/file from schema
        node_object = self.load_schema(self, meta_object, node_object)
        # Populate URL field (common to file and dataset?)
        ds_info = next((item for item in meta_object[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
                        # TODO: CHECK IF THIS ONLY GETS RUL FIELD FOR DATASET!!!
        if ds_info and cnst.DISTRIBUTION in ds_info:
            origin = next((item for item in ds_info[cnst.DISTRIBUTION]
                        if cnst.NAME in item and item[cnst.NAME] == cnst.ORIGIN), False)
            if origin:
                node_object[cnst.URL] = origin[cnst.URL]
        # Add dataset-specific fields
        if self.type == cnst.TYPE_DATASET:
            self.dataset_translator(self, meta_object, node_object)
        # Add extractor type to 



    def dataset_translator(self, meta_object, node_object):
        """
        Parse dataset-level metadata output by DataLad's `metalad_core` extractor
        """
        ds_info = next((item for item in meta_object[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
        # Populate subdatasets field
        node_object[cnst.SUBDATASETS] = []
        if ds_info and cnst.HASPART in ds_info:
            for subds in ds_info[cnst.HASPART]:
                sub_dict = {
                    cnst.DATASET_ID: subds[cnst.IDENTIFIER].strip(cnst.STRIPDATALAD),
                    cnst.DATASET_VERSION: subds[cnst.ATID].strip(cnst.STRIPDATALAD),
                    cnst.DATASET_PATH: subds[cnst.NAME],
                    cnst.DIRSFROMPATH: list(Path(subds[cnst.NAME]).parts)
                }
                node_object[cnst.SUBDATASETS].append(sub_dict)

        # Populate extractor field
        extractor_dict = {
            cnst.EXTRACTOR_NAME: meta_object[cnst.EXTRACTOR_NAME],
            cnst.EXTRACTOR_VERSION: subds[cnst.ATID].strip(cnst.STRIPDATALAD),
            cnst.DATASET_PATH: subds[cnst.NAME],
            cnst.DIRSFROMPATH: list(Path(subds[cnst.NAME]).parts)
        }
        # "extractor_name": "metalad_core", "extractor_version": "1", "extraction_parameter": {}, "extraction_time": 1636623469.594389,
        return node_object


class StudyminimetaTranslator(Translator):
    """"""

    def __init__(self, meta_object, node_object) -> None:
        self.schema_file = self.package_path / cnst.SCHEMA_STUDYMINIMETA

#     metadata = {}
#     # Extract core objects/lists from src_object
#     metadata["study"] = next((item for item
#                               in src_object["extracted_metadata"]["@graph"]
#                               if "@type" in item
#                               and item["@type"] == "CreativeWork"), False)
#     if not metadata["study"]:
#         print("Warning: object where '@type' equals 'CreativeWork' not found in \
# src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    
#     metadata["dataset"] = next((item for item
#                                 in src_object["extracted_metadata"]["@graph"]
#                                 if "@type" in item
#                                 and item["@type"] == "Dataset"), False)
#     if not metadata["dataset"]:
#         print("Warning: object where '@type' equals 'Dataset' not found in \
# src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    
#     metadata["publicationList"] = \
#         next((item for item in src_object["extracted_metadata"]["@graph"]
#               if "@id" in item and item["@id"] == "#publicationList"), False)
#     if not metadata["publicationList"]:
#         print("Warning: object where '@id' equals '#publicationList' not found \
# in src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
#     else:
#         metadata["publicationList"] = metadata["publicationList"]["@list"]
    
#     metadata["personList"] = \
#         next((item for item in src_object["extracted_metadata"]["@graph"]
#               if "@id" in item and item["@id"] == "#personList"), False)
#     if not metadata["personList"]:
#         print("Warning: object where '@id' equals '#personList' not found in \
# src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
#     else:
#         metadata["personList"] = metadata["personList"]["@list"]
    
#     # Standard/straightforward fields: copy source to dest values per key
#     for key in schema:
#         if isinstance(schema[key], list) and len(schema[key]) == 2:
#             if schema[key][0] in metadata \
#                and schema[key][1] in metadata[schema[key][0]]:
#                 dest_object[key] = metadata[schema[key][0]][schema[key][1]]
#         else:
#             dest_object[key] = schema[key]
#     # Description
#     dest_object["description"] = dest_object["description"].replace('<', '')
#     dest_object["description"] = dest_object["description"].replace('>', '')
#     # Authors
#     for author in metadata["dataset"]["author"]:
#         author_details = \
#             next((item for item in metadata["personList"]
#                   if item["@id"] == author["@id"]), False)
#         if not author_details:
#             idd = author["@id"]
#             print(f"Error: Person details not found in '#personList' for '@id'={idd}")
#         else:
#             dest_object["authors"].append(author_details)
#     # Publications
#     if metadata["publicationList"]:
#         for pub in metadata["publicationList"]:
#             new_pub = {"type" if k == "@type" else k: v for k, v in pub.items()}
#             new_pub = {"doi" if k == "sameAs"
#                     else k: v for k, v in new_pub.items()}
#             new_pub["publication"] = {"type" if k == "@type"
#                                     else k: v for k, v in new_pub.items()}
#             if "@id" in new_pub:
#                 new_pub.pop("@id")
#             if "@id" in new_pub["publication"]:
#                 new_pub["publication"].pop("@id")
#             for i, author in enumerate(new_pub["author"]):
#                 author_details = \
#                     next((item for item in metadata["personList"]
#                         if item["@id"] == author["@id"]), False)
#                 if not author_details:
#                     idd = author["@id"]
#                     print(f"Error: Person details not found in '#personList' for\
#                         @id = {idd}")
#                 else:
#                     new_pub["author"][i] = author_details
#             dest_object["publications"].append(new_pub)
#     return dest_object


class CoreDatasetTranslator(Translator):
    """"""

    def __init__(self, meta_object, node_object) -> None:
        pass