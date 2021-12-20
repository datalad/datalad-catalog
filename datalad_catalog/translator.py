# from abc import ABC, abstractmethod
from pathlib import Path
from . import constants as cnst
from .webcatalog import WebCatalog, Node, getNode
from .utils import read_json_file
from datalad.interface.results import get_status_dict
import logging

lgr = logging.getLogger('datalad.catalog.translator')


class Translator(object):
    """
    Translate a single metadata item from its raw state (output by datalad metalad,
    input to datalad catalog) into a node, set of nodes, and/or child of a node.

    This class takes care of the delineation of a metadata item into nodes based on
    the item type (dataset / file) and the path of the item.

    It then directs input to the relevant callable based on the type of extractor used.    
    """

    # Get package-related paths/content
    package_path = Path(__file__).resolve().parent
    templates_path = package_path / 'templates'

    def __init__(self) -> None:
        pass

    def __call__(self, catalog: WebCatalog, meta_item: dict):
        """
        Get meta_item type: dataset or file
        For dataset: create dataset node object and call relevant translator
        For file: 
        """
        # Get dataset id and version
        d_id = meta_item[cnst.DATASET_ID]
        d_version = meta_item[cnst.DATASET_VERSION]
        # get metadata object type (dataset or file)
        if meta_item[cnst.TYPE] == cnst.TYPE_DATASET:
            # If dataset, create special node
            # TODO: this does not take into account that a dataset might have a path with mupltiple directories
            node_instance = getNode("dataset", dataset_id=d_id, dataset_version=d_version)
            # TODO: handle unrecognised extractors
            translated_dict = cnst.EXTRACTOR_TRANSLATOR_SELECTOR.get(meta_item[cnst.EXTRACTOR_NAME])(meta_item, node_instance)
            # Add translated_dict to node instance; TODO: handle duplications (overwrite for now)
            node_instance.addAttribrutes(translated_dict, overwrite=True)
            # Add extractor info
            node_instance.addAttribrutes(self.get_extractor_info(meta_item), overwrite=True)
        else:
            # If file: create standard node per path part
            f_path = meta_item[cnst.PATH]
            parts_in_path = list(Path(f_path.lstrip('/')).parts)
            nr_of_dirs = len(parts_in_path)-1 # this excludes the last part, which is the actual filename
            incremental_path = Path('')
            # Assume for now that we're working purely with class instances during operation, then write to file at end
            # IMPORTANT: this does not account for files that already exist, and their content ==> TODO
            for part_count, part in enumerate(parts_in_path):
                # Get node path
                incremental_path = incremental_path / part
                # when reaching the filename, add it as child to parent node
                if part_count == nr_of_dirs:
                    # Get node object with parent path (it would have been created already)
                    node_instance = getNode(dataset_id=d_id, dataset_version=d_version, node_path=parts_in_path[part_count-1])
                    # TODO: handle unrecognised extractors
                    # TODO: decide on useful way to return translated info
                    translated_dict = cnst.EXTRACTOR_TRANSLATOR_SELECTOR.get(meta_item[cnst.EXTRACTOR_NAME])(meta_item)
                    # TODO: perhaps instance method for adding children?
                    # TODO: perhaps instance method for copying data from dict to node?
                    node_instance.children.append(translated_dict)
                # for all other parts in the path
                else:
                    # Instantiate/get node object
                    node_instance = getNode(dataset_id=d_id, dataset_version=d_version, node_path=incremental_path)

    def load_schema(self, meta_item, dest_dict):
        schema = read_json_file(self.schema_file)
        # Copy source to destination values, per key
        for key in schema:
            if schema[key] in meta_item:
                dest_dict[key] = meta_item[schema[key]]
        return dest_dict

    def get_extractor_info(meta_item):
        return {
            cnst.EXTRACTOR_NAME: meta_item[cnst.EXTRACTOR_NAME],
            cnst.EXTRACTOR_VERSION: meta_item[cnst.EXTRACTOR_VERSION],
            }


class CoreTranslator(Translator):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    Could be dataset- or file-level metadata
    Returns a dictionary
    """

    def __init__(self, meta_item, node_instance=None) -> dict:
        """"""
        # Initialise empty dictionary to hold translated data
        self.meta_dict = {}

        # Assign schema file for dataset/file
        self.type = meta_item[cnst.TYPE]
        if meta_item[cnst.TYPE] == cnst.TYPE_DATASET:
            self.schema_file = self.package_path / cnst.SCHEMA_CORE_FOR_DATASET
        else:
            self.schema_file = self.package_path / cnst.SCHEMA_CORE_FOR_FILE
        # Load basic fields for dataset/file from schema
        self.load_schema(self, meta_item, self.meta_dict)
        
        # Populate fields common to dataset and file:
        # URL:
        ds_info = next((item for item in meta_item[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
                        # TODO: CHECK IF THIS ONLY GETS URL FIELD FOR DATASET!!!
        if ds_info and cnst.DISTRIBUTION in ds_info:
            origin = next((item for item in ds_info[cnst.DISTRIBUTION]
                        if cnst.NAME in item and item[cnst.NAME] == cnst.ORIGIN), False)
            if origin:
                self.meta_dict[cnst.URL] = origin[cnst.URL]

        # Add dataset-specific fields
        if self.type == cnst.TYPE_DATASET:
            self.dataset_translator(self, meta_item, node_instance)

        return self.meta_dict

    def dataset_translator(self, meta_item, node_instance):
        """
        Parse dataset-level metadata output by DataLad's `metalad_core` extractor
        """
        # Access relevant metadata from item
        ds_info = next((item for item in meta_item[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
        # Populate subdatasets field
        # TODO: add subdatasets as children too!!!!
        self.meta_dict[cnst.SUBDATASETS] = []
        if ds_info and cnst.HASPART in ds_info:
            for subds in ds_info[cnst.HASPART]:
                # Append subdataset
                parts_in_path = list(Path(subds[cnst.NAME].lstrip('/')).parts)
                subds_id = subds[cnst.IDENTIFIER].strip(cnst.STRIPDATALAD)
                subds_version = subds[cnst.ATID].strip(cnst.STRIPDATALAD)
                sub_dict = {
                    cnst.DATASET_ID: subds_id,
                    cnst.DATASET_VERSION: subds_version,
                    cnst.DATASET_PATH: subds[cnst.NAME],
                    cnst.DIRSFROMPATH: parts_in_path
                }
                self.meta_dict[cnst.SUBDATASETS].append(sub_dict)
                # Create node per directory in subdataset
                if len(parts_in_path) > 1:
                    self.dataset_path_to_nodes(parts_in_path, subds_id, subds_version)
                else:
                    node_instance.children.append(translated_dict)

    def dataset_path_to_nodes(self, parts_in_path, d_id, d_version):
        """"""
        nr_of_dirs = len(parts_in_path)-1 # this excludes the last part, which is the dataset
        incremental_path = Path('')
        # Assume for now that we're working purely with class instances during operation, then write to file at end
        # IMPORTANT: this does not account for files that already exist, and their content ==> TODO
        for part_count, part in enumerate(parts_in_path):
            # Get node path
            incremental_path = incremental_path / part
            # when reaching the filename, add it as child to parent node
            if part_count == nr_of_dirs:
                # Get node object with parent path (it would have been created already)
                node_instance = getNode(dataset_id=d_id, dataset_version=d_version, node_path=parts_in_path[part_count-1])
                # TODO: perhaps instance method for adding children?
                # TODO: perhaps instance method for copying data from dict to node?
                node_instance.children.append(translated_dict)
            # for all other parts in the path
            else:
                # Instantiate/get node object
                node_instance = getNode(dataset_id=d_id, dataset_version=d_version, node_path=incremental_path)



class StudyminimetaTranslator(Translator):
    """"""

    def __init__(self, meta_item, node_instance=None) -> dict:
        """"""
        # Initialise empty dictionary to hold translated data, and temporary data
        self.meta_dict = {}
        self.temp_meta_item = {}
        # Load basic fields for dataset from schema
        self.schema_file = self.package_path / cnst.SCHEMA_STUDYMINIMETA
        # Extract core dicts/lists from raw meta_item
        # "study"
        self._load_temp_info(self, cnst.STUDY, cnst.CREATIVEWORK, meta_item)
        # "Dataset"
        self._load_temp_info(self, cnst.DATASET, cnst.DATASET, meta_item)
        # "publicationList"
        self._load_temp_info(self, cnst.PUBLICATIONLIST, cnst.PUBLICATIONLIST, meta_item)
        # "personList"
        self._load_temp_info(self, cnst.PERSONLIST, cnst.PERSONLIST, meta_item)
        # Load basic metadata (dependend on fields existing in self.temp_meta_item)
        # (note: ot using self.load_schema because different steps are required here)
        self.load_studyminimeta_schema(self)
        # Remove unwanted characters from "description"
        self.meta_dict[cnst.DESCRIPTION] = self.meta_dict[cnst.DESCRIPTION].replace('<', '')
        self.meta_dict[cnst.DESCRIPTION] = self.meta_dict[cnst.DESCRIPTION].replace('>', '')
        # Move authors into list
        self._move_authors()
        # Move publications into list
        if self.temp_meta_item[cnst.PUBLICATIONLIST]:
            self._move_publications()
        return self.meta_dict

    def load_studyminimeta_schema(self):
        """"""
        schema = read_json_file(self.schema_file)
        for key in schema:
            if isinstance(schema[key], list) and len(schema[key]) == 2:
                if schema[key][0] in self.temp_meta_item \
                and schema[key][1] in self.temp_meta_item[schema[key][0]]:
                    self.meta_dict[key] = self.temp_meta_item[schema[key][0]][schema[key][1]]
            else:
                self.meta_dict[key] = schema[key]

    def _load_temp_info(self, new_key, lookfor_key, meta_item):
        """"""
        self.temp_meta_item[new_key] = \
            next((item for item in meta_item[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                  if cnst.ATTYPE in item and item[cnst.ATTYPE] == lookfor_key), False)
        if not self.temp_meta_item[cnst.STUDY]:
            message = f"Warning: object where '@type' equals '{lookfor_key}' not found in \
                meta_item['extracted_metadata']['@graph'] during studyminimeta extraction"
            lgr.warning(message)
        else:
            if new_key in [cnst.PERSONLIST, cnst.PUBLICATIONLIST]:
                self.temp_meta_item[new_key] = self.temp_meta_item[new_key][cnst.ATLIST]
            else:
                pass

    def _move_authors(self):
        """"""
        for author in self.temp_meta_item[cnst.TYPE_DATASET][cnst.AUTHOR]:
            author_details = next((item for item in self.temp_meta_item[cnst.PERSONLIST]
                                   if item[cnst.ATID] == author[cnst.ATID]), False)
            if not author_details:
                idd = author[cnst.ATID]
                message=f"Error: Person details not found in '#personList' for '@id'={idd}"
                lgr.warning(message)
            else:
                self.meta_dict[cnst.AUTHORS].append(author_details)

    def _move_publications(self):
        """"""
        for pub in self.temp_meta_item[cnst.PUBLICATIONLIST]:
            # First remove/replace some unwanted characters
            new_pub = {cnst.TYPE if k == cnst.ATTYPE else k: v for k, v in pub.items()}
            new_pub = {cnst.DOI if k == cnst.SAMEAS else k: v for k, v in new_pub.items()}
            new_pub[cnst.PUBLICATION] = {cnst.TYPE if k == cnst.ATTYPE
                                            else k: v for k, v in new_pub.items()}
            if cnst.ATID in new_pub:
                new_pub.pop(cnst.ATID)
            if cnst.ATID in new_pub[cnst.PUBLICATION]:
                new_pub[cnst.PUBLICATION].pop(cnst.ATID)
            # Then move all into a list
            for i, author in enumerate(new_pub[cnst.AUTHOR]):
                author_details = \
                    next((item for item in self.temp_meta_item[cnst.PERSONLIST]
                        if item[cnst.ATID] == author[cnst.ATID]), False)
                if not author_details:
                    idd = author[cnst.ATID]
                    message=f"Error: Person details not found in '#personList' for '@id'={idd}"
                    lgr.warning(message)
                else:
                    new_pub[cnst.AUTHOR][i] = author_details
            self.meta_dict[cnst.PUBLICATIONS].append(new_pub)


class CoreDatasetTranslator(Translator):
    """"""
    def __init__(self, meta_item, node_instance=None) -> None:
        pass