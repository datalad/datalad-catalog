# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Translate datacite_gin-based metadata to the catalog schema"""
import jq
import logging
from pathlib import Path
from datalad_catalog.translate import TranslatorBase

lgr = logging.getLogger("datalad.metadata.translators.datacite_gin_translator")

class DataciteGINTranslator(TranslatorBase):
    """
    Translate metadata extracted with metalad and the datacite_gin extractor
    to the catalog schema

    Inherits from base class TranslatorBase.
    """
    def __init__(self):
        pass

    def get_supported_schema_version(self):
        """
        Reports the version of the catalog schema supported by the translator
        """
        return "0.1.0"

    def get_supported_extractor_name(self):
        """
        Reports the name of the extractor supported by the translator
        """
        return "datacite_gin"

    def get_supported_extractor_version(self):
        """
        Reports the version of the extractor supported by the translator
        """
        return "0.0.1"

    def translate(self, metadata: dict) -> dict:
        """
        Translates incoming metadata into the catalog schema
        """
        return DataciteTranslator(metadata).translate()


class DataciteTranslator:
    """Translator for datacite_gin
    Uses jq programs written by jsheunis for datalad-catalog workflow
    to translate some fields. Will not include empty values in its output.
    """

    def __init__(self, metadata_record):
        self.metadata_record = metadata_record
        self.extracted_metadata = self.metadata_record["extracted_metadata"]

    def get_name(self):
        return self.extracted_metadata.get("title", "")

    def get_description(self):
        return self.extracted_metadata.get("description")

    def get_license(self):
        program = ".license | { \"name\": .name, \"url\": .url}"
        result = jq.first(program, self.extracted_metadata)
        # todo check for license info missing
        return result if len(result) > 0 else None

    def get_authors(self):
        program = (
            "[.authors[]? | "
            "{\"name\":\"\", \"givenName\":.firstname, \"familyName\":.lastname"
            ", \"email\":\"\", \"honorificSuffix\":\"\"} "
            "+ if has(\"id\") then {\"identifiers\":[ "
            "{\"type\":(.id | tostring | split(\":\") | .[0]),"
            " \"identifier\":(.id | tostring | split(\":\") | .[1])}]} "
            "else null end]"
        )
        result = jq.first(program, self.extracted_metadata)
        return result if len(result) > 0 else None

    def get_keywords(self):
        return self.extracted_metadata.get("keywords")

    def get_funding(self):
        program = (
            "[.funding[]? as $element | "
            "{\"name\": $element, \"identifier\": \"\", \"description\": \"\"}]"
        )
        result = jq.first(program, self.extracted_metadata)

    def get_publications(self):
        program = (
            "[.references[]? as $pubin | "
            "{\"type\":\"\", "
            "\"title\":$pubin[\"citation\"], "
            "\"doi\":"
            "($pubin[\"id\"] | sub(\"DOI:\"; \"https://www.doi.org/\")), "
            "\"datePublished\":\"\", "
            "\"publicationOutlet\":\"\", "
            "\"authors\": []}]"
        )
        result = jq.first(program, self.extracted_metadata)

    def get_extractors_used(self):
        keys = [
            "extractor_name", "extractor_version",
            "extraction_parameter", "extraction_time",
            "agent_name", "agent_email",
        ]
        return [{k: self.metadata_record[k] for k in keys}]

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
            "publications": self.get_publications(),
            "extractors_used": self.get_extractors_used(),
        }
        return {k: v for k, v in translated_record.items() if v is not None}