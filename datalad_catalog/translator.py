# from abc import ABC, abstractmethod
from pathlib import Path
from . import constants as cnst
from .webcatalog import WebCatalog, Node, getNode
from .utils import read_json_file
from datalad.interface.results import get_status_dict
import logging

lgr = logging.getLogger('datalad.catalog.translator')

EXTRACTOR_CORE="metalad_core"
EXTRACTOR_CORE_DATASET="metalad_core_dataset"
EXTRACTOR_NAME="extractor_name"
EXTRACTOR_STUDYMINIMETA="metalad_studyminimeta"


def getTranslator(extractor_name):
    """"""
    if extractor_name == EXTRACTOR_CORE:
        return CoreTranslator
    elif extractor_name == EXTRACTOR_CORE_DATASET:
        return CoreTranslator
    elif extractor_name == EXTRACTOR_STUDYMINIMETA:
        return StudyminimetaTranslator
    else:
        print("UNRECOGNIZED METADTA EXTRACTOR PRESENT. TODO: RAISE EXCEPTION")
        """"""


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

    def __init__(self, catalog: WebCatalog, meta_item: dict) -> None:
        print("In Translator")
        # Get dataset id and version
        d_id = meta_item[cnst.DATASET_ID]
        d_version = meta_item[cnst.DATASET_VERSION]
        # For both dataset and file, we need the dataset node (fetch / create):
        dataset_instance = getNode("dataset", dataset_id=d_id, dataset_version=d_version)
        # set parent catalog
        if not hasattr(dataset_instance, 'parent_catalog') or not dataset_instance.parent_catalog:
            dataset_instance.parent_catalog = catalog
        # Then call specific translator
        # TODO: handle unrecognised extractors
        translated_dict = getTranslator(meta_item[cnst.EXTRACTOR_NAME])(meta_item).meta_dict
        # Then do things based on metadata object type (dataset or file)
        if meta_item[cnst.TYPE] == cnst.TYPE_DATASET:
            # Dataset
            self.process_dataset(dataset_instance, translated_dict, meta_item, catalog)
        else:
            # File
            # TODO: confirm what to do if meta_item for file from dataset arrives before meta_item for dataset
            # For now: creating node for dataset, even if via file meta_item.
            print("TRanslated dict before process file")
            print(translated_dict)
            self.process_file(dataset_instance, translated_dict, meta_item, catalog)

    def __call__(self):
        """
        """
        pass
        
    def process_dataset(self, dataset_instance, translated_dict, meta_item, catalog):
        """"""
        # Add translated_dict to node instance; TODO: handle duplications (overwrite for now)
        dataset_instance.add_attribrutes(translated_dict, overwrite=True)
        # Add missing information TODO.
        self.add_missing_fields(dataset_instance)
        # Add extractor info

        dataset_instance.add_extractor(self.get_extractor_info(meta_item))
    
    def process_file(self, dataset_instance: Node, translated_dict, meta_item, catalog):
        """"""
        print("In Translator.process_file")
        #  Create standard node per path part; TODO: when adding file as child, also add translated_dict
        f_path = meta_item[cnst.PATH]
        parts_in_path = list(Path(f_path.lstrip('/')).parts)
        nr_parts = len(parts_in_path)
        print(f_path)
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
                cnst.DATASET_ID: dataset_instance.dataset_id,
                cnst.DATASET_VERSION: dataset_instance.dataset_version,
            }
            print(f"i = {i}")
            if i == 0 and nr_parts == 1:
                # If the file has no parent directories other than the dataset,
                # add file as child to dataset node
                translated_dict.update(file_dict)
                dataset_instance.add_child(translated_dict)
                print(translated_dict)
                break

            # If the file has one or more parent directories
            if i == 0:
                # first dir in path, add as child to dataset node
                dataset_instance.add_child(dir_dict)
            elif 0 < i < nr_dirs:
                # 2nd...(N-1)th dir in path: create node for N-1, add current as child (dir) to node: bv i=1, create node for i=0
                node_instance = getNode("directory",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.parent_catalog = catalog
                node_instance.add_child(dir_dict)
            else:
                # Nth (last) part in path = file: create node for N-1, add current as child (file) to node
                extractor_info = {}
                extractor_info["extractors_used"] = []
                extractor_info["extractors_used"].append(self.get_extractor_info(meta_item))
                translated_dict.update(file_dict)
                translated_dict.update(extractor_info)
                node_instance = getNode("directory",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.parent_catalog = catalog
                node_instance.add_child(translated_dict)
            print(translated_dict)
            # print(dataset_instance.add_child(translated_dict))

    def get_extractor_info(self, meta_item):
        return {
            cnst.EXTRACTOR_NAME: meta_item[cnst.EXTRACTOR_NAME],
            cnst.EXTRACTOR_VERSION: meta_item[cnst.EXTRACTOR_VERSION],
            cnst.EXTRACTION_PARAMETER: meta_item[cnst.EXTRACTION_PARAMETER],
            cnst.EXTRACTION_TIME: meta_item[cnst.EXTRACTION_TIME],
        }
    
    def add_missing_fields(self, dataset_instance):
        """
        Add fields to a dataset object that are required for UI but are not yet
        contained in the object, i.e. not available in any Datalad extractor output
        or not yet parsed for the specific dataset
        """
        pass
        # if "name" not in dataset_instance and "dataset_path" in dataset_instance:
        #     dataset_instance["name"] = dataset_instance["dataset_path"]. \
        #                             split(os.path.sep)[-1]
        # if "name" in dataset_instance and "short_name" not in dataset_instance:
        #     if len(dataset_instance["name"]) > 30:
        #         dataset_instance["short_name"] = dataset_instance["name"][0:30]+'...'
        #     else:
        #         dataset_instance["short_name"] = dataset_instance["name"]

        # schema = load_json_file(os.path.join(schema_path,
        #                                     "studyminimeta_empty.json"))
        # for key in schema:
        #     if key not in dataset_instance:
        #         dataset_instance[key] = schema[key]

        # if "children" not in dataset_instance:
        #     dataset_instance["children"] = []

        # if "subdatasets" not in dataset_instance:
        #     dataset_instance["subdatasets"] = []

        # return dataset_object


class CoreTranslator(object):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    Could be dataset- or file-level metadata
    Returns a dictionary
    """

    def __init__(self, meta_item) -> None:
        """"""
        print("In CoreTranslator")
        # Initialise empty dictionary to hold translated data
        if not hasattr(self, 'meta_dict') or self.meta_dict is None:
            print("set metadict to empty dict")
            self.meta_dict = {}

        # Assign schema file for dataset/file
        self.type = meta_item[cnst.TYPE]
        if meta_item[cnst.TYPE] == cnst.TYPE_DATASET:
            self.schema_file = Translator.package_path / 'templates' / cnst.SCHEMA_CORE_FOR_DATASET
        else:
            self.schema_file = Translator.package_path / 'templates' / cnst.SCHEMA_CORE_FOR_FILE
        # Load basic fields for dataset/file from schema

        load_schema(self.schema_file, meta_item, self.meta_dict)
        # Add dataset-specific fields
        if self.type == cnst.TYPE_DATASET:
            self.dataset_translator(meta_item)
        else:
            self.file_translator(meta_item)

    def file_translator(self, meta_item):
        """"""
        print("In CoreTranslator.file_translator")
        self.meta_dict[cnst.CONTENTBYTESIZE] = ''
        if cnst.CONTENTBYTESIZE in meta_item[cnst.EXTRACTED_METADATA]:
            self.meta_dict[cnst.CONTENTBYTESIZE] = meta_item[cnst.EXTRACTED_METADATA][cnst.CONTENTBYTESIZE]

        self.meta_dict[cnst.URL] = ''
        if cnst.DISTRIBUTION in meta_item[cnst.EXTRACTED_METADATA] and cnst.URL in meta_item[cnst.EXTRACTED_METADATA][cnst.DISTRIBUTION]:
            self.meta_dict[cnst.URL] = meta_item[cnst.EXTRACTED_METADATA][cnst.DISTRIBUTION][cnst.URL]

    def dataset_translator(self, meta_item):
        """
        Parse dataset-level metadata output by DataLad's `metalad_core` extractor
        """
        print("In CoreTranslator.dataset_translator")
        d_id = meta_item[cnst.DATASET_ID]
        d_version = meta_item[cnst.DATASET_VERSION]
        dataset_instance = getNode("dataset", dataset_id=d_id, dataset_version=d_version)
        # Access relevant metadata from item
        ds_info = next((item for item in meta_item[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
        # Add URL field
        self.meta_dict[cnst.URL] = ''
        if ds_info and cnst.DISTRIBUTION in ds_info:
            origin = next((item for item in ds_info[cnst.DISTRIBUTION]
                        if cnst.NAME in item and item[cnst.NAME] == cnst.ORIGIN), False)
            if origin:
                self.meta_dict[cnst.URL] = origin[cnst.URL]
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
                    dataset_instance.add_child(subds_dict)

    def subdataset_path_to_nodes(self, dataset_instance: Node, parts_in_path, subds_id, subds_version):
        """
        Add parts of subdataset paths as nodes and children where relevant
        Function used when path to subdataset (relative to parent dataset) has multiple parts
        """
        print("In CoreTranslator.subdataset_path_to_nodes")
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
                dataset_instance.add_child(dir_dict)
            elif i < nr_parts-1:
                # 2nd...(N-1)th dir in path: create node for N-1, add current as child (dir) to node: bv i=1, create node for i=0
                # path for i: parent_dirs[nr_parts-1-i]
                node_instance = getNode("directory",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.add_child(dir_dict)
            else:
                # Nth (last) part in path = sub-dataset: create node for N-1, add current as child (dataset) to node
                subds_dict = {
                    cnst.TYPE: cnst.TYPE_DATASET,
                    cnst.NAME: part,
                    cnst.PATH: str(incremental_path),
                    cnst.DATASET_ID: subds_id,
                    cnst.DATASET_VERSION: subds_version,
                }
                node_instance = getNode("directory",
                                        dataset_id=dataset_instance.dataset_id,
                                        dataset_version=dataset_instance.dataset_version,
                                        path=paths[i-1])
                node_instance.add_child(subds_dict)


class StudyminimetaTranslator(object):
    """"""

    def __init__(self, meta_item, node_instance=None) -> None:
        """"""
        print("In StudyminimetaTranslator")
        # Initialise empty dictionary to hold translated data, and temporary data
        if not hasattr(self, 'meta_dict') or self.meta_dict is None:
            print("set metadict to empty dict")
            self.meta_dict = {}
        self.temp_meta_item = {}
        # Load basic fields for dataset from schema
        self.schema_file = Translator.package_path / 'templates' / cnst.SCHEMA_STUDYMINIMETA
        # Extract core dicts/lists from raw meta_item
        # "study"
        self._load_temp_info(cnst.STUDY, cnst.CREATIVEWORK, meta_item)
        # "Dataset"
        self._load_temp_info(cnst.TYPE_DATASET, cnst.DATASET, meta_item)
        # "publicationList"
        self._load_temp_info(cnst.PUBLICATIONLIST, cnst.PUBLICATIONLIST, meta_item)
        # "personList"
        self._load_temp_info(cnst.PERSONLIST, cnst.PERSONLIST, meta_item)
        # print("Metadict")
        # print(self.meta_dict)
        # print("Temp Metadict")
        # print(self.temp_meta_item)
        # Load basic metadata (dependend on fields existing in self.temp_meta_item)
        # (note: ot using self.load_schema because different steps are required here)
        self.load_studyminimeta_schema()
        # Remove unwanted characters from "description"
        self.meta_dict[cnst.DESCRIPTION] = self.meta_dict[cnst.DESCRIPTION].replace('<', '')
        self.meta_dict[cnst.DESCRIPTION] = self.meta_dict[cnst.DESCRIPTION].replace('>', '')
        # Move authors into list
        if self.temp_meta_item[cnst.PERSONLIST]:
            self._move_authors()
        # Move publications into list
        if self.temp_meta_item[cnst.PUBLICATIONLIST]:
            self._move_publications()

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
        key = cnst.ATTYPE
        if lookfor_key in [cnst.PERSONLIST, cnst.PUBLICATIONLIST]:
            key = cnst.ATID

        self.temp_meta_item[new_key] = \
            next((item for item in meta_item[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                  if key in item and item[key] == lookfor_key), False)
        
        if not self.temp_meta_item[new_key]:
            message = (f"Warning: object where '{key}' equals '{lookfor_key}' not found in"
                " meta_item['extracted_metadata']['@graph'] during studyminimeta extraction")
            lgr.warning(message)
        else:
            if new_key in [cnst.PERSONLIST, cnst.PUBLICATIONLIST]:
                if self.temp_meta_item[new_key]:
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


class CoreDatasetTranslator(object):
    """
    Parse metadata output by DataLad's `metalad_core_dataset` extractor and
    translate into JSON structure from which UI is generated.
    Could be dataset- or file-level metadata
    Returns a dictionary
    """

    def __init__(self, meta_item) -> None:
        """"""
        raise NotImplementedError

def load_schema(schema_file, src, dest):
    schema = read_json_file(schema_file)
    # Copy source to destination values, per key
    for key in schema:
        if schema[key] in src:
            dest[key] = src[schema[key]]
    return dest