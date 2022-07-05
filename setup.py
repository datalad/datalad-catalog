#!/usr/bin/env python

import sys
from setuptools import setup
import versioneer

from _datalad_buildsupport.setup import (
    BuildManPage,
)

cmdclass = versioneer.get_cmdclass()
cmdclass.update(build_manpage=BuildManPage)

# Give setuptools a hint to complain if it's too old a version
# 43.0.0 allows us to put most metadata in setup.cfg and causes pyproject.toml
# to be automatically included in sdists
# Should match pyproject.toml
SETUP_REQUIRES = ["setuptools >= 43.0.0"]
# This enables setuptools to install wheel on-the-fly
SETUP_REQUIRES += ["wheel"] if "bdist_wheel" in sys.argv else []

if __name__ == "__main__":
    setup(
        name="datalad_catalog",
        version=versioneer.get_version(),
        cmdclass=cmdclass,
        setup_requires=SETUP_REQUIRES,
        entry_points={
            "datalad.extensions": [
                "catalog=datalad_catalog:command_suite",
            ],
            "datalad.tests": ["catalog=datalad_catalog"],
            "datalad.metadata.extractors": [
                "datacite_gin=datalad_catalog.extractors.datacite_gin:DataciteGINDatasetExtractor",
            ],
        },
    )
