import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="datalad_catalog",
    version="0.1.0",
    description="Generate a web-based data browser from a DataLad dataset's metadata",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jsheunis/data-browser-from-metadata",
    author="DataLad developers",
    license="MIT",
    packages=["datalad_catalog"],
    include_package_data=True,
    # install_requires=["feedparser", "html2text"],
    entry_points={
        "console_scripts": [
            'datalad_catalog = datalad_catalog.webui_generate:run_cmd',
            ]
    },
)