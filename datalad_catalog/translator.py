# from abc import ABC, abstractmethod
from pathlib import Path
from . import constants as cnst
from .webcatalog import Dataset, WebCatalog, Node, getNode
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
        """
        # Get dataset id and version
        d_id = meta_item[cnst.DATASET_ID]
        d_version = meta_item[cnst.DATASET_VERSION]
        # For both dataset and file, we need the dataset node (fetch / create):
        dataset_instance = getNode("dataset", dataset_id=d_id, dataset_version=d_version)
        # Then call specific translator
        # TODO: handle unrecognised extractors
        translated_dict = cnst.EXTRACTOR_TRANSLATOR_SELECTOR.get(meta_item[cnst.EXTRACTOR_NAME])(meta_item)
        # Then do things based on metadata object type (dataset or file)
        if meta_item[cnst.TYPE] == cnst.TYPE_DATASET:
            # Dataset
            self.process_dataset(dataset_instance, translated_dict, meta_item, catalog)
        else:
            # File
            # TODO: confirm what to do if meta_item for file from dataset arrives before meta_item for dataset
            # For now: creating node for dataset, even if via file meta_item.
            self.process_file(dataset_instance, translated_dict, meta_item, catalog)

    def process_dataset(self, dataset_instance, translated_dict, meta_item, catalog):
        """"""
        # Add translated_dict to node instance; TODO: handle duplications (overwrite for now)
        dataset_instance.addAttribrutes(translated_dict, overwrite=True)
        # Add missing information TODO.
        self.add_missing_fields(self, dataset_instance)
        # Add extractor info
        dataset_instance.addAttribrutes(self.get_extractor_info(meta_item), overwrite=True)
        # Make sure that dataset instance belongs to catalog
        dataset_instance.parent_catalog = catalog
    
    def process_file(self, dataset_instance, translated_dict, meta_item, catalog):
        """"""
        #  Create standard node per path part; TODO: when adding file as child, also add translated_dict
        f_path = meta_item[cnst.PATH]
        parts_in_path = list(Path(f_path.lstrip('/')).parts)
        nr_parts = len(parts_in_path)
        nr_dirs = nr_parts-1 # this excludes the last part, which is the actual filename
        incremental_path = Path('')
        paths = []
        # Assume for now that we're working purely with class instances during operation, then write to file at end
        # IMPORTANT: this does not account for files that already exist, and their content ==> TODO
        for i, part in enumerate(parts_in_path):
            # Get node path
            incremental_path = incremental_path / part
            paths.append(incremental_path)
            file_dict = {
                cnst.TYPE: cnst.TYPE_FILE,
                cnst.NAME: part,
                cnst.PATH: str(incremental_path),
            }
            dir_dict = {
                cnst.TYPE: cnst.TYPE_DIRECTORY,
                cnst.NAME: part,
                cnst.PATH: str(incremental_path),
            }
            if i == 0 and nr_parts == 1:
                # If the file has no parent directories other than the dataset,
                # add file as child to dataset node
                translated_dict.update(file_dict)
                dataset_instance.children.append(translated_dict)
                break
            # If the file has one or more parent directories
            if i == 0:
                # first dir in path, add as child to dataset node
                translated_dict.update(dir_dict)
                dataset_instance.children.append(dir_dict)
            elif i < nr_parts:
                # 2nd...(N-1)th dir in path: create node for N-1, add current as child (dir) to node: bv i=1, create node for i=0
                # path for i: parent_dirs[nr_parts-1-i]
                translated_dict.update(dir_dict)
                node_instance = getNode("node",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.parent_catalog = catalog
                node_instance.children.append(translated_dict)
            else:
                # Nth (last) part in path = file: create node for N-1, add current as child (file) to node
                translated_dict.update(file_dict)
                node_instance = getNode("node",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.parent_catalog = catalog
                node_instance.children.append(translated_dict)
    
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
    
    def add_missing_fields(self, dataset_object):
        """
        Add fields to a dataset object that are required for UI but are not yet
        contained in the object, i.e. not available in any Datalad extractor output
        or not yet parsed for the specific dataset
        """
        pass
        # if "name" not in dataset_object and "dataset_path" in dataset_object:
        #     dataset_object["name"] = dataset_object["dataset_path"]. \
        #                             split(os.path.sep)[-1]
        # if "name" in dataset_object and "short_name" not in dataset_object:
        #     if len(dataset_object["name"]) > 30:
        #         dataset_object["short_name"] = dataset_object["name"][0:30]+'...'
        #     else:
        #         dataset_object["short_name"] = dataset_object["name"]

        # schema = load_json_file(os.path.join(schema_path,
        #                                     "studyminimeta_empty.json"))
        # for key in schema:
        #     if key not in dataset_object:
        #         dataset_object[key] = schema[key]

        # if "children" not in dataset_object:
        #     dataset_object["children"] = []

        # if "subdatasets" not in dataset_object:
        #     dataset_object["subdatasets"] = []

        # return dataset_object


class CoreTranslator(Translator):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    Could be dataset- or file-level metadata
    Returns a dictionary
    """

    def __init__(self, meta_item) -> dict:
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
            self.dataset_translator(self, meta_item)

        return self.meta_dict

    def dataset_translator(self, meta_item):
        """
        Parse dataset-level metadata output by DataLad's `metalad_core` extractor
        """
        d_id = meta_item[cnst.DATASET_ID]
        d_version = meta_item[cnst.DATASET_VERSION]
        dataset_instance = getNode("dataset", dataset_id=d_id, dataset_version=d_version)
        # Access relevant metadata from item
        ds_info = next((item for item in meta_item[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
        # Populate subdatasets field
        # TODO: add subdatasets as children too!!!!
        self.meta_dict[cnst.SUBDATASETS] = []
        if ds_info and cnst.HASPART in ds_info:
            for subds in ds_info[cnst.HASPART]:
                # Construct subdataset dictionary: id, version, path, dirsfrompath
                p = Path(subds[cnst.NAME].lstrip('/'))
                parts_in_path = list(p.parts)
                subds_id = subds[cnst.IDENTIFIER].strip(cnst.STRIPDATALAD)
                subds_version = subds[cnst.ATID].strip(cnst.STRIPDATALAD)
                sub_dict = {
                    cnst.DATASET_ID: subds_id,
                    cnst.DATASET_VERSION: subds_version,
                    cnst.DATASET_PATH: subds[cnst.NAME],
                    cnst.DIRSFROMPATH: parts_in_path
                }
                # append dict to subdatasets list (an attribute of Node instance)
                self.meta_dict[cnst.SUBDATASETS].append(sub_dict)
                # Create node per directory in subdataset
                if len(parts_in_path) > 1:
                    self.subdataset_path_to_nodes(dataset_instance, parts_in_path, subds_id, subds_version)
                else:
                    subds_dict = {
                        cnst.TYPE: cnst.TYPE_DATASET,
                        cnst.NAME: subds[cnst.NAME],
                        cnst.DATASET_ID: subds_id,
                        cnst.DATASET_VERSION: subds_version,
                    }
                    dataset_instance.children.append(subds_dict)

    def subdataset_path_to_nodes(self, dataset_instance: Dataset, parts_in_path, subds_id, subds_version):
        """
        Add parts of subdataset paths as nodes and children where relevant
        Function used when path to subdataset (relative to parent dataset) has multiple parts
        """
        nr_parts = len(parts_in_path)
        incremental_path = Path('')
        paths = []
        # IMPORTANT: this does not account for files that already exist, and their content ==> TODO
        for i, part in enumerate(parts_in_path):
            # Create dictionary of type directory
            incremental_path = incremental_path / part
            paths.append(incremental_path)
            dir_dict = {
                cnst.TYPE: cnst.TYPE_DIRECTORY,
                cnst.NAME: part,
                cnst.PATH: str(incremental_path),
            }
            if i == 0:
                # first dir in path, add as child to dataset node
                dataset_instance.children.append(dir_dict)
            elif i < nr_parts:
                # 2nd...(N-1)th dir in path: create node for N-1, add current as child (dir) to node: bv i=1, create node for i=0
                # path for i: parent_dirs[nr_parts-1-i]
                node_instance = getNode("node",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.children.append(dir_dict)
            else:
                # Nth (last) part in path = sub-dataset: create node for N-1, add current as child (dataset) to node
                subds_dict = {
                    cnst.TYPE: cnst.TYPE_DATASET,
                    cnst.NAME: part,
                    cnst.PATH: str(incremental_path),
                    cnst.DATASET_ID: subds_id,
                    cnst.DATASET_VERSION: subds_version,
                }
                node_instance = getNode("node",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.children.append(subds_dict)


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