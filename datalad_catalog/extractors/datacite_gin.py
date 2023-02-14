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
import yaml
from pathlib import Path
from uuid import UUID

from datalad_metalad.extractors.base import (
    DatasetMetadataExtractor,
    DataOutputCategory,
    ExtractorResult,
)
from datalad_metalad.extractors.legacy.definitions import vocabulary_id
from datalad.log import log_progress
from datalad.utils import ensure_unicode


lgr = logging.getLogger("datalad.metadata.extractors.datacite_gin")

# From metalad legacy; TODO: remove/replace when it becomes useful
# identifiers that defines an ontology as a whole
vocabulary_id = "http://purl.org/dc/dcam/VocabularyEncodingScheme"

datacite_context = {
    "@id": "https://gin.g-node.org/G-Node/Info/src/master/datacite.yml",
    "description": "ad-hoc vocabulary for the DataCite GIN yml format",
    "type": vocabulary_id,
}


class DataciteGINDatasetExtractor(DatasetMetadataExtractor):
    """
    Inherits from metalad's DatasetMetadataExtractor class
    """

    datacite_yaml_file_name = "datacite.yml"

    def get_id(self) -> UUID:
        # Note sure what the process should be for generating these
        # Just took another UUID and made some characters 1
        return UUID("111487ea-e670-4801-bcdc-29639bf10111")

    def get_version(self) -> str:
        return "0.0.1"

    def get_data_output_category(self) -> DataOutputCategory:
        return DataOutputCategory.IMMEDIATE

    def get_required_content(self) -> bool:
        result = self.dataset.get(
            self.datacite_yaml_file_name, result_renderer="disabled"
        )
        return result[0]["status"] in ("ok", "notneeded")

    def extract(self, _=None) -> ExtractorResult:
        return ExtractorResult(
            extractor_version=self.get_version(),
            extraction_parameter=self.parameter or {},
            extraction_success=True,
            datalad_result_dict={"type": "dataset", "status": "ok"},
            immediate_data=DataciteGINMeta(self.dataset).get_metadata(),
        )


class DataciteGINMeta(object):
    """
    The Datacite GIN metadata extractor class that does the work
    """

    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def _get_datacite_yml_file_path(self) -> Path:
        return Path(self.dataset.path) / "datacite.yml"

    def get_metadata(self):
        """
        Function to load data and run metadata extraction+translation
        """
        log_progress(
            lgr.info,
            "extractorsdatacitegin",
            "Start datacite_gin metadata extraction from {path}".format(
                path=self.dataset.path
            ),
            total=len(tuple("ok")) + 1,
            label="datacite_gin metadata extraction",
            unit=" Files",
        )

        # Get datacite.yml file
        datacite_file_path = self._get_datacite_yml_file_path()
        if not datacite_file_path.exists():
            msg = f"File {datacite_file_path} could not be found"
            lgr.warning(msg)
            return
        # Read metadata from file
        with open(datacite_file_path, "rt") as input_stream:
            metadata_object = yaml.safe_load(input_stream)
        return self._get_dsmeta(metadata_object)

    def _get_dsmeta(self, metadata):
        """"""
        # Format the description
        metadata["description"] = self._get_description(metadata["description"])
        # add context
        metadata["@context"] = datacite_context
        # For now, keep all other fields as they are. Might format/translate in
        # the future. See:
        # https://github.com/datalad/datalad-metalad/issues/202#issuecomment-1024192167
        return metadata

    def _get_description(self, description_in):
        """"""
        desc = ensure_unicode(description_in)
        return desc.strip()
