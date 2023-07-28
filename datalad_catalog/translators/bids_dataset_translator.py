# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Translate bids_dataset-based metadata to the catalog schema"""
import jq
import logging
from pathlib import Path
from datalad_catalog.translate import TranslatorBase

lgr = logging.getLogger("datalad.metadata.translators.bids_dataset_translator")


class BIDSDatasetTranslator(TranslatorBase):
    """
    Translate metadata extracted with metalad and the bids_dataset extractor
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
        return "bids_dataset"

    @classmethod
    def get_supported_extractor_version(self):
        """
        Reports the version of the extractor supported by the translator
        """
        return "0.0.1"

    def translate(self, metadata: dict) -> dict:
        """
        Translates incoming metadata into the catalog schema
        """
        return BIDSTranslator(metadata).translate()


class BIDSTranslator:
    """Translator for bids_dataset
    Uses jq programs written by jsheunis for datalad-catalog workflow
    to translate some fields. Will not include empty values in its output.
    """

    def __init__(self, metadata_record):
        self.metadata_record = metadata_record
        self.extracted_metadata = self.metadata_record["extracted_metadata"]

    def get_name(self):
        return self.extracted_metadata.get("Name", "")

    def get_description(self):
        bids_description = self.extracted_metadata.get("description")
        if isinstance(bids_description, str):
            return bids_description
        elif isinstance(bids_description, list):
            if len(bids_description) > 0:
                # bids_description expected format = [{"extension": "", "text": "",}]
                # TODO: figure out which extension has priority;
                # take 1st element for now
                return bids_description[0].get("text", None)
            else:
                return None
        else:
            return None

    def get_license(self):
        url_map = {
            # only the licenses & links explicitly named in bids spec
            "PDDL": "https://opendatacommons.org/licenses/pddl/",
            "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
        }
        license_name = self.extracted_metadata.get("License")
        if license_name is not None:
            return {"name": license_name, "url": url_map.get(license_name, "")}
        return None

    def get_authors(self):
        program = (
            "[.Authors[]? as $auth | "
            '{"name": $auth, "givenName":"", "familyName":"", '
            '"email":"", "honorificSuffix":"", "identifiers":[]}]'
        )
        result = jq.first(program, self.extracted_metadata)
        return result if len(result) > 0 else None

    def get_keywords(self):
        program = ". as $parent | .entities.task + .variables.dataset"
        result = jq.first(program, self.extracted_metadata)
        return result if len(result) > 0 else None

    def get_funding(self):
        program = (
            "[.Funding[]? as $fund | "
            '{"name": "", "grant":"", "description":$fund}]'
        )
        result = jq.first(program, self.extracted_metadata)
        return result if len(result) > 0 else None

    def get_publications(self):
        program = (
            "[.references[]? as $pubin | "
            '{"type":"", '
            '"title":$pubin["citation"], '
            '"doi":'
            '($pubin["id"] | sub("DOI:"; "https://www.doi.org/")), '
            '"datePublished":"", '
            '"publicationOutlet":"", '
            '"authors": []}]'
        )
        result = jq.first(program, self.extracted_metadata)
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

    def get_additional_display(self):
        program = '[{"name": "BIDS", "content": .entities}]'
        result = jq.first(program, self.extracted_metadata)
        return result if len(result) > 0 else None

    def get_top_display(self):
        program = (
            '[{"name": "Subjects", "value": (.entities.subject | length)}, '
            '{"name": "Sessions", "value": (.entities.session | length)}, '
            '{"name": "Tasks", "value": (.entities.task | length)}, '
            '{"name": "Runs", "value": (.entities.run | length)}]'
        )
        result = jq.first(program, self.extracted_metadata)
        return result if len(result) > 0 else None

    def translate(self):
        translated_record = {
            "type": self.metadata_record["type"],
            "dataset_id": self.metadata_record["dataset_id"],
            "dataset_version": self.metadata_record["dataset_version"],
            "name": self.get_name(),
            "description": self.get_description(),
            "authors": self.get_authors(),
            "keywords": self.get_keywords(),
            "funding": self.get_funding(),
            "license": self.get_license(),
            "metadata_sources": self.get_metadata_source(),
            "additional_display": self.get_additional_display(),
            "top_display": self.get_top_display(),
        }
        return {k: v for k, v in translated_record.items() if v is not None}
