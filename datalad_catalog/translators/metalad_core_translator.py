# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Translate metalad_core-based metadata to the catalog schema"""
import jq
import logging
from pathlib import Path
from datalad_catalog.translate import TranslatorBase

lgr = logging.getLogger("datalad.metadata.translators.metalad_core_translator")


class MetaladCoreTranslator(TranslatorBase):
    """
    Translate metadata extracted with metalad and the metalad_core extractor
    to the catalog schema

    Inherits from base class TranslatorBase.
    """

    def __init__(self):
        pass

    def match(
        cls,
        schema_version: str,
        source_name: str,
        source_version: str,
        source_id: str = None,
    ) -> bool:
        """
        Matching routine for the current translator

        Parameters
        ----------
        source_name: str
            The name of the metadata extractor/source
        source_version: str
            The version of the metadata extractor/source
        source_id: str, optional
            The unique extractor/source ID. Defaults to None.

        Returns
        -------
            bool
                True if the match is successful, else False.
        """

        extractor_name_match = cls.get_supported_extractor_name() == source_name
        extractor_version_match = (
            cls.get_supported_extractor_version() == source_version
        )
        schema_version_match = (
            cls.get_supported_schema_version() == schema_version
        )
        # TODO: support partial matches of version (major/minor/patch)

        return (
            extractor_name_match
            & extractor_version_match
            & schema_version_match
        )

    @classmethod
    def get_supported_schema_version(self):
        """
        Reports the version of the catalog schema supported by the translator
        """
        return "1.0.0"

    @classmethod
    def get_supported_extractor_name(self):
        """
        Reports the name of the extractor supported by the translator
        """
        return "metalad_core"

    @classmethod
    def get_supported_extractor_version(self):
        """
        Reports the version of the extractor supported by the translator
        """
        return "1"

    def translate(self, metadata: dict) -> dict:
        """
        Translates incoming metadata into the catalog schema
        """
        return CoreTranslator(metadata).translate()


class CoreTranslator:
    """Translator for metalad_core
    Uses jq programs written by jsheunis for datalad-catalog workflow
    to translate some fields. Will not include empty values in its output.
    """

    def __init__(self, metadata_record):
        self.metadata_record = metadata_record
        self.extracted_metadata = self.metadata_record["extracted_metadata"]
        self.graph = self.extracted_metadata.get("@graph", [])

    def get_name(self):
        """Return an empty string as name

        Name is not a property of a DataLad dataset, but it is required
        by the catalog. We return an empty string to satisfy validation.
        """
        return ""

    def get_dataset_url(self):
        program = (
            '.[]? | select(.["@type"] == "Dataset") | '
            '[.distribution[]? | select(has("url")) | .url]'
        )
        return jq.first(program, self.graph)

    def get_authors(self):
        program = (
            '[.[]? | select(.["@type"]=="agent")] | '
            'map(del(.["@id"], .["@type"]))'
        )
        return jq.first(program, self.graph)

    def get_subdatasets(self):
        program = (
            '.[]? | select(.["@type"] == "Dataset") | '
            "[.hasPart[]? | "
            '{"dataset_id": (.["identifier"] // "" | '
            'sub("^datalad:"; "")), "dataset_version": (.["@id"] | '
            'sub("^datalad:"; "")), "dataset_path": .["name"], '
            '"dirs_from_path": []}]'
        )
        result = jq.first(program, self.graph)
        return result if len(result) > 0 else None

    def get_metadata_source(self):
        program = (
            '{"key_source_map": {},"sources": [{'
            '"source_name": .extractor_name, '
            '"source_version": .extractor_version, '
            '"source_parameter": .extraction_parameter, '
            '"source_time": .extraction_time, '
            '"agent_email": .agent_email, '
            '"agent_name": .agent_name}]}'
        )
        result = jq.first(program, self.metadata_record)
        return result if len(result) > 0 else None

    def get_file_url(self):
        program = ".distribution? | .url?"
        return jq.first(program, self.extracted_metadata)

    def get_file_path(self):
        return self.metadata_record.get("path", None)

    def get_contentbytesize(self):
        return self.extracted_metadata.get("contentbytesize", None)

    def translate(self):
        translated_record = {
            "type": self.metadata_record["type"],
            "dataset_id": self.metadata_record["dataset_id"],
            "dataset_version": self.metadata_record["dataset_version"],
            "metadata_sources": self.get_metadata_source(),
        }
        if translated_record["type"] == "dataset":
            translated_record.update(
                {
                    "name": self.get_name(),
                    "url": self.get_dataset_url(),
                    "authors": self.get_authors(),
                    "subdatasets": self.get_subdatasets(),
                }
            )
        if translated_record["type"] == "file":
            translated_record.update(
                {
                    "path": self.get_file_path(),
                    "url": self.get_file_url(),
                    "contentbytesize": self.get_contentbytesize(),
                }
            )

        return {k: v for k, v in translated_record.items() if v is not None}
