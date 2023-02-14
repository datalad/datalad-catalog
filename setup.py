#!/usr/bin/env python

import sys
from setuptools import setup
import versioneer

from _datalad_buildsupport.setup import (
    BuildManPage,
)

cmdclass = versioneer.get_cmdclass()
cmdclass.update(build_manpage=BuildManPage)

if __name__ == "__main__":
    setup(
        name="datalad_catalog",
        version=versioneer.get_version(),
        cmdclass=cmdclass,
    )
