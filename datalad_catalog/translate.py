# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Translate metalad-extracted metadata items into the catalog schema
"""

import datalad_catalog.constants as cnst
from datalad_catalog.constraints import (
    EnsureWebCatalog,
    metadata_constraint,
)
from datalad_catalog.utils import (
    EntryPointsNotFoundError,
    get_available_entrypoints,
    jsEncoder,
)
from datalad_catalog.validate import get_schema_store
from datalad_catalog.webcatalog import (
    WebCatalog,
)
from datalad_next.commands import (
    EnsureCommandParameterization,
    ValidatedInterface,
    Parameter,
    build_doc,
    eval_results,
    get_status_dict,
)
from datalad_next.exceptions import CapturedException
from datalad_next.uis import ui_switcher
from datalad.support.exceptions import InsufficientArgumentsError

import abc
import json
import logging
import os


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.meta_translate")


class MetaTranslateParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=EnsureWebCatalog(),
                metadata=metadata_constraint,
            ),
            joint_constraints=dict(),
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class MetaTranslate(ValidatedInterface):
    """Translate datalad-metalad-extracted metadata items into the catalog schema

    The to-be-translated-to schema version is determined from the catalog,
    if provided, otherwise from the latest supported version of the package installation.

    Tranlators should be provided and exposed as a datalad entry point using the group:
    'datalad.metadata.translators'.

    Available translators will be filtered based on own matching criteria (such as
    extractor name, version, etc) to find the appropriate translator, after which
    the translator's translation code will be executed on the metadata item.
    """

    _validator_ = MetaTranslateParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of an existing catalog. If this argument
            is provided it will determine the to-be-translated-to 
            schema version. If the version cannot be found in the 
            catalog, it is determined from the latest supported version
            of the package installation. The latter is also the default
            when the 'catalog' argument is not supplied.""",
        ),
        metadata=Parameter(
            # cmdline argument definitions, incl aliases
            args=("metadata",),
            # documentation
            doc="""The metalad-extracted metadata that is to be translated.
            Multiple input types are possible:
            - a path to a file containing JSON lines
            - JSON lines from STDIN
            - a JSON serialized string""",
        ),
    )

    _examples_ = [
        dict(
            text=(
                "Translate a metalad-extracted metadata item from a particular "
                "source structure into the catalog schema, assuming a dedicated "
                "translator is locally available via the entry point mechanism"
            ),
            code_py=(
                "catalog_translate(catalog='/tmp/my-cat', "
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog-translate -c /tmp/my-cat -m path/to/metadata.jsonl"
            ),
        ),
    ]

    @staticmethod
    def custom_result_renderer(res, **kwargs):
        """This result renderer dumps the value of the 'output' key
        in the result record in JSON-line format -- only if status==ok"""
        ui = ui_switcher.ui
        ui.message(
            json.dumps(
                res.get("translated_metadata"),
                separators=(",", ":"),
                indent=None,
                cls=jsEncoder,
            )
        )

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        metadata,
        catalog=None,
    ):
        # 1. Argument handling
        # 1a. metadata
        # input validation allows for a JSON-serialized string
        # handled by EnsureJSON (which seems to return a dict)
        # -> turn this into a list for uniform processing below
        if isinstance(metadata, (str, dict)):
            metadata = [metadata]
        # 1b. catalog
        # If the catalog argument is provided, ensure that the
        # catalog is instantiated correctly
        if catalog is not None:
            # Instantiate WebCatalog class if necessary
            if not isinstance(catalog, WebCatalog):
                catalog = WebCatalog(
                    location=catalog,
                )
        # get relevant catalog schema version
        # schema store is returned from catalog if provided, else package
        schema_store = get_schema_store(catalog)
        schema_id = cnst.CATALOG_SCHEMA_IDS[cnst.CATALOG]
        schema_version = schema_store[schema_id][cnst.VERSION]
        # 2. Get all available translators via entrypoints:
        try:
            all_translators = get_available_entrypoints(group="translators")
            loaded_translators = []
        except EntryPointsNotFoundError as e:
            err_msg = (
                "No translators found: there are no translators available "
                "to the current environment. Relevant translators have to be "
                "made available via datalad's entrypoint mechanism in order for "
                "the catalog-translate command to recognize them."
            )
            yield get_status_dict(
                **res_kwargs,
                status="impossible",
                message=err_msg,
                exception=e,
            )
        # 3. Prepare standard arguments for result record
        res_kwargs = dict(
            action="catalog_translate",
            path=catalog.location if catalog is not None else os.getcwd(),
        )
        # 4. Process each line of metadata
        for i, line in enumerate(metadata):
            if isinstance(line, CapturedException):
                # the generator encountered an exception for a particular
                # item and is relaying it as per instructions
                # exc_mode='yield'. We report and move on. Outside
                # flow logic will decide if processing continues
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    exception=line,
                )
                continue
            # load json object into dict
            if isinstance(line, str):
                meta_dict = json.loads(line.rstrip())
            else:
                meta_dict = line
            # Check if line is a dict
            if not isinstance(meta_dict, dict):
                err_msg = (
                    "Metadata item not of type dict: metadata items should be "
                    "passed to datalad-catalog as JSON objects adhering to the "
                    "catalog schema."
                )
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    message=err_msg,
                )
                continue
            # Translate dict
            try:
                translated_meta = Translate(
                    meta_record=meta_dict,
                    schema_version=schema_version,
                    available_translators=all_translators,
                    loaded_translators=loaded_translators,
                ).run_translator()

                yield get_status_dict(
                    **res_kwargs,
                    status="ok",
                    message=("Metadata successfully translated"),
                    translated_metadata=translated_meta,
                )
            except Exception as e:
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    exception=e,
                )


class Translate(object):
    """
    Class responsible for executing translation of an extracted metadata record,
    including finding a matching class (base class TranslatorBase) and running
    metadata translation.
    """

    def __init__(
        self,
        meta_record: dict,
        schema_version: str,
        available_translators: dict = {},
        loaded_translators: list = [],
    ) -> None:
        """"""
        # instantiate
        self.meta_record = meta_record
        self.schema_version = schema_version
        self.available_translators = available_translators
        self.loaded_translators = loaded_translators
        self.match_translator()

    def match_translator(self):
        """Match an extracted metadata record with an appropriate translator

        Parameters
        ----------
        meta_record : dict
            A dictionary containing metadata that was extracted from a file or dataset
            using datalad-metalad

        Returns
        ------
        TranslatorBase
            The first matched translator instance of base class TranslatorBase
        """
        # First get source name and version from record
        source_name = self.meta_record.get(cnst.EXTRACTOR_NAME)
        source_version = self.meta_record.get(cnst.EXTRACTOR_VERSION)
        # If the relevant translator has already been matched and loaded,
        # access it
        matched_loaded = [
            t
            for t in self.loaded_translators
            if t.get("source_name") == source_name
            and t.get("source_version") == source_version
            and t.get("schema_version") == self.schema_version
        ]
        if len(matched_loaded) > 0:
            self.translator = matched_loaded[0].get("translator_instance")
        else:
            # Else run through all translators and run their matching methods
            matched_translators = []
            for (
                translator_name,
                translator_dict,
            ) in self.available_translators.items():
                translator_class = translator_dict["loader"]()
                translator_instance = translator_class()
                if translator_instance.match(
                    self.schema_version, source_name, source_version
                ):
                    # break on first match
                    matched_translators.append(translator_instance)
                    break
            # Raise error if there was no match
            if not matched_translators:
                self.translator = None
                raise TranslatorNotFoundError(
                    "Metadata translator not found for metadata source "
                    f"{source_name} and version {source_version}"
                )
            # if for some reason more than one entry points are returned
            # select first one
            self.translator = matched_translators[0]
            self.loaded_translators.append(
                {
                    "translator_name": translator_name,
                    "source_name": source_name,
                    "source_version": source_version,
                    "schema_version": self.schema_version,
                    "translator_instance": self.translator,
                }
            )

    def run_translator(self):
        """"""
        return self.translator.translate(self.meta_record)


class TranslatorNotFoundError(InsufficientArgumentsError):
    pass


class TranslatorBase(metaclass=abc.ABCMeta):
    """
    Translator base class providing internal methods for matching
    incoming metadata to a translator that inherits from this base class,
    as well as the following abstract methods that should be overridden
    by the inheriting class:
        match()
        translate()
    """

    @classmethod
    @abc.abstractmethod
    def match(
        cls,
        schema_version: str,
        source_name: str,
        source_version: str,
        source_id: str = None,
    ) -> bool:
        """
        Report the result of matching criteria applied to the translator

        This tests whether the inherited translator can be used to translate
        metadata output from a specific source.

        Current criteria include extractor name and extractor version,
        and the catalog schema version
        """
        raise NotImplementedError

    @abc.abstractmethod
    def translate(self, metadata):
        """
        Translate incoming metadata to the current catalog schema

        This method contains the logic for translating an incoming metadata
        object to the catalog schema (version-specific).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_supported_schema_version(self):
        """
        Reports the version of the catalog schema supported by the translator
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_supported_extractor_name(self):
        """
        Reports the name of the extractor supported by the translator
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_supported_extractor_version(self):
        """
        Reports the version of the extractor supported by the translator
        """
        raise NotImplementedError
