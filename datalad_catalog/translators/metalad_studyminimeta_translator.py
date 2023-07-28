# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Translate metalad_studyminimeta-based metadata to the catalog schema"""
import jq
import logging
from pathlib import Path
from datalad_catalog.translate import TranslatorBase

lgr = logging.getLogger(
    "datalad.metadata.translators.metalad_studyminimeta_translator"
)


class MetaladStudyminimetaTranslator(TranslatorBase):
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
        return "metalad_studyminimeta"

    @classmethod
    def get_supported_extractor_version(self):
        """
        Reports the version of the extractor supported by the translator
        """
        return "0.1"

    def translate(self, metadata: dict) -> dict:
        """
        Translates incoming metadata into the catalog schema
        """
        return MinimetaTranslator(metadata).translate()


class MinimetaTranslator:
    """Translator for metalad_studyminimeta
    Uses jq programs written by jsheunis for datalad-catalog workflow
    to translate some fields, but introduces additional condition checks.
    Will not include empty values in its output.
    """

    def __init__(self, metadata_record):
        self.metadata_record = metadata_record
        self.extracted_metadata = self.metadata_record["extracted_metadata"]

        self.graph = self.extracted_metadata["@graph"]
        self.type_dataset = jq.first(
            '.[] | select(.["@type"] == "Dataset")',
            self.graph,
        )
        self.combinedpersonsids = self._jq_first_or_none(
            program=(
                '{"authordetails": .[] | '
                'select(.["@id"] == "#personList") | '
                '.["@list"], "authorids": .[] | '
                'select(.["@type"] == "Dataset") | .author}'
            ),
            entry=self.graph,
        )
        self.combinedpersonspubs = self._jq_first_or_none(
            program=(
                '{"authordetails": .[] | '
                'select(.["@id"] == "#personList") | '
                '.["@list"], "publications": .[] | '
                'select(.["@id"] == "#publicationList") | .["@list"]}'
            ),
            entry=self.graph,
        )

    def _jq_first_or_none(self, program, entry):
        try:
            result = jq.first(program, entry)
        except StopIteration:
            result = None
        return result

    def get_name(self):
        return self.type_dataset.get("name", "")

    def get_description(self):
        return self.type_dataset.get("description")

    def get_url(self):
        return self.type_dataset.get("url")

    def get_keywords(self):
        return self.type_dataset.get("keywords")

    def get_authors(self):
        if self.combinedpersonsids is not None:
            program = (
                '. as $parent | [.authorids[]["@id"] as $idin | '
                '($parent.authordetails[] | select(.["@id"] == $idin))]'
            )
            return jq.first(program, self.combinedpersonsids)
        return None

    def get_funding(self):
        program = (
            '.[] | select(.["@type"] == "Dataset") | [.funder[]? | '
            '{"name": .name, "identifier": "", "description": ""}]'
        )
        result = jq.first(program, self.graph)  #  [] if nothing found
        return result if len(result) > 0 else None

    def get_publications(self):
        if self.combinedpersonspubs is not None:
            program = (
                ". as $parent | [.publications[] as $pubin | "
                '{"type":$pubin["@type"], '
                '"title":$pubin["headline"], '
                '"doi":$pubin["sameAs"], '
                '"datePublished":$pubin["datePublished"], '
                '"publicationOutlet":$pubin["publication"]["name"], '
                '"authors": ([$pubin.author[]["@id"] as $idin | '
                '($parent.authordetails[] | select(.["@id"] == $idin))])}]'
            )
            return jq.first(program, self.combinedpersonspubs)
        else:
            return None

    def get_subdatasets(self):
        program = (
            '.[]? | select(.["@type"] == "Dataset") | [.hasPart[]? | '
            '{"dataset_id": (.identifier | sub("^datalad:"; "")), '
            '"dataset_version": (.["@id"] | sub("^datalad:"; "")), '
            '"dataset_path": .name, "dirs_from_path": []}]'
        )
        result = jq.first(program, self.graph)  #  [] if nothing found
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

    def translate(self):
        translated_record = {
            "type": self.metadata_record["type"],
            "dataset_id": self.metadata_record["dataset_id"],
            "dataset_version": self.metadata_record["dataset_version"],
            "name": self.get_name(),
            "description": self.get_description(),
            "url": self.get_url(),
            "authors": self.get_authors(),
            "keywords": self.get_keywords(),
            "funding": self.get_funding(),
            "publications": self.get_publications(),
            "subdatasets": self.get_subdatasets(),
            "metadata_sources": self.get_metadata_source(),
        }

        return {k: v for k, v in translated_record.items() if v is not None}
