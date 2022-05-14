# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Metadata extractor for GIN-flavored datacite.yml information"""
import logging
from uuid import UUID
from pathlib import Path
import yaml
from datalad_metalad.extractors.base import DataOutputCategory, ExtractorResult, DatasetMetadataExtractor
from datalad.log import log_progress
from datalad.metadata.definitions import vocabulary_id
from datalad.utils import assure_unicode

lgr = logging.getLogger('datalad.metadata.extractors.datacite_gin')

vocabulary = {
}

# Main properties used in GIN-based datacite.yml
class DATACITE_PROPERTIES:
    # REQUIRED FIELDS
    AUTHORS = "authors"
    FIRSTNAME = "firstname"
    LASTNAME = "lastname"
    AFFILIATION = "affiliation"
    ID = "id" # CAN HAVE A TYPE: ORCID, RESEARCHERID
    ORCID = "ORCID"
    RESEARCHERID = "ResearcherID"
    TITLE = "title"
    DESCRIPTION = "description"
    KEYWORDS = "keywords"
    LICENSE = "license"
    NAME = "name" # OF LICENSE
    URL = "url" # OF LICENSE
    # OPTIONAL FIELDS
    FUNDING = "funding" # FUNDER, GRANT NR
    REFERENCES = "references" # ID CAN BE: DOI, arxiv, pmid
    CITATION = "citation"
    DOI = "DOI" 
    REFTYPE = "reftype" # CAN BE: IsSupplementTo, IsDescribedBy, IsReferencedBy.
    ISSUPPLEMENTTO = "IsSupplementTo"
    ISDESCRIBEDBY = "IsDescribedBy"
    ISREFERENCEDBY = "IsReferencedBy"
    RESOURCETYPE = "resourcetype" # Default is Dataset, can also be: Software, Image, Text
    TEMPLATEVERSION = "templateversion"

DATACITECONTEXT = {
    "@id": "https://gin.g-node.org/G-Node/Info/src/master/datacite.yml",
    'description': 'ad-hoc vocabulary for the DataCite GIN yml format',
    'type': vocabulary_id,
}

DATASET = 'dataset'

# DATACITE_PROPERTIES_MAPPING= {
#     # DATACITE_PROPERTIES.AUTHORS: DATACITE_PROPERTIES.AUTHORS,
#     DATACITE_PROPERTIES.TITLE: SMMSchemaOrgProperties.NAME,
#     DATACITE_PROPERTIES.DESCRIPTION: SMMSchemaOrgProperties.DESCRIPTION,
#     DATACITE_PROPERTIES.KEYWORDS: SMMSchemaOrgProperties.KEYWORDS,
#     DATACITE_PROPERTIES.LICENSE: DATACITE_PROPERTIES.LICENSE,
#     DATACITE_PROPERTIES.FUNDING: DATACITE_PROPERTIES.FUNDING,
#     DATACITE_PROPERTIES.REFERENCES: DATACITE_PROPERTIES.REFERENCES,
#     DATACITE_PROPERTIES.RESOURCETYPE: DATACITE_PROPERTIES.RESOURCETYPE,
# }

# required_keys = DATACITE_PROPERTIES_MAPPING[:4]
# optional_keys = DATACITE_PROPERTIES_MAPPING[4:]


class DataciteGINDatasetExtractor(DatasetMetadataExtractor):
    """
    Inherits from metalad's DatasetMetadataExtractor class
    """

    def get_id(self) -> UUID:
        # Note sure what the process should be for generating these
        # Just took another UUID and made some characters 1
        return UUID("111487ea-e670-4801-bcdc-29639bf10111")

    def get_version(self) -> str:
        return "0.0.1"

    def get_data_output_category(self) -> DataOutputCategory:
        return DataOutputCategory.IMMEDIATE

    def get_required_content(self) -> bool:
        return False

    def extract(self, _=None) -> ExtractorResult:
        return ExtractorResult(
            extractor_version=self.get_version(),
            extraction_parameter=self.parameter or {},
            extraction_success=True,
            datalad_result_dict={
                "type": "dataset",
                "status": "ok"
            },
            immediate_data=DataciteGINmeta(self.dataset).get_metadata())

class DataciteGINmeta(object):
    """
    The Datacite GIN metadata extractor class that does the work
    """

    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def _get_datacite_yml_file_name(self):
        return Path(self.dataset.path) / 'datacite.yml'        

    def get_metadata(self):
        """
        Function to load data and run metadata extraction+translation
        """
        log_progress(
            lgr.info,
            'extractorsdatacitegin',
            'Start datacite_gin metadata extraction from {path}'.format(path=self.dataset.path),
            total=len(tuple('ok')) + 1,
            label='datacite_gin metadata extraction',
            unit=' Files',
        )

        # Get datacite.yml file
        self.datacite_fn = self._get_datacite_yml_file_name()
        if not self.datacite_fn.exists():
            msg = "File " + str(self.datacite_fn) + " could not be found"
            lgr.warning(msg)
            return
        # Read metadata from file
        with open(self.datacite_fn, "rt") as input_stream:
            metadata_object = yaml.safe_load(input_stream)
        # try:
        #     with open(self.datacite_fn, "rt") as input_stream:
        #         metadata_object = yaml.safe_load(input_stream)
        #         print(metadata_object)
        # except FileNotFoundError:
        #     msg = "file " + self.datacite_fn + " could not be opened"
            
        #     yield {
        #         "status": "error",
        #         "metadata": {},
        #         "type": "dataset",
        #         "message": msg
        #     }
        #     return
        # except yaml.YAMLError as e:
        #     yield {
        #         "status": "error",
        #         "metadata": {},
        #         "type": "dataset",
        #         "message": "YAML parsing failed with: " + str(e)
        #     }
        #     return

        # Write metadata fields into new dict
        metadata = {k: v for k, v in metadata_object.items()}
        return self._get_dsmeta(metadata)
    
    def _get_dsmeta(self, metadata):
        """"""
        # Format the description
        metadata['description'] = self._get_description(metadata['description'])
        # add context
        metadata['@context'] = DATACITECONTEXT     
        # For now, keep all other fields as the are. Might format/translate in future
        # See: https://github.com/datalad/datalad-metalad/issues/202#issuecomment-1024192167
        return metadata
    
    def _get_description(self, description_in):
        """"""
        desc = assure_unicode(description_in)
        return desc.strip()