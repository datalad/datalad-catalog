## --- UNDER DEVELOPMENT ---
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
*This repository is undergoing continuous development and all branches should be considered unstable*

---


[![Documentation Status](https://readthedocs.org/projects/datalad-catalog/badge/?version=latest)](http://docs.datalad.org/projects/catalog/en/latest/?badge=latest)

![](docs/source/_static/datacat0_hero.svg)

<br>

DataLad Catalog is a free and open source command line tool, with a Python API, that assists with the automatic generation of user-friendly, browser-based data catalogs from structured metadata. It is an extension to [DataLad](https://datalad.org) and forms part of the broader ecosystem of DataLad's distributed metadata handling and (meta)data publishing tools.

## 1. Online demo

Navigate to [https://datalad.github.io/datalad-catalog/](https://datalad.github.io/datalad-catalog/) to view a live demo of a catalog generated with DataLad Catalog.

This demo site is hosted via GitHub Pages and it builds from the `gh-pages` branch of this repository.

<div style="text-align:center;">
    <img src="docs/source/_static/datalad_catalog_demo.svg" width="75%"></img>
</div>

## 2. How it works

DataLad Catalog can receive commands to `create` a new catalog, `add` and `remove` metadata entries to/from an existing catalog, `serve` an existing catalog locally, and more. Metadata can be provided to DataLad Catalog from any number of arbitrary metadata sources, as an aggregated set or as individual metadata items. DataLad Catalog has a dedicated schema (using the [JSON Schema](https://json-schema.org/) vocabulary) against which incoming metadata items are validated. This schema allows for standard metadata fields as one would expect for datasets of any kind (such as `name`, `doi`, `url`, `description`, `license`, `authors`, and more), as well as fields that support identification, versioning, dataset context and linkage, and file tree specification.

The process of generating a catalog, after metadata entry validation, involves:
1. aggregation of the provided metadata into the catalog filetree, and
2. generating the assets required to render the user interface in a browser.

The output is a set of structured metadata files, as well as a [Vue.js](https://vuejs.org/)-based browser interface that understands how to render this metadata in the browser. What is left for the user is to host this content on their platform of choice and to serve it for the world to see.

<br>
<div style="text-align:center;">
    <img src="docs/source/_static/datacat4_the_catalog.svg" width="75%"></img>
</div>


## 3. Install `datalad-catalog`

### Step 1 - Setup and activate virtual environment

With your virtual environment manager of choice, create a virtual environment and ensure
you have a recent version of Python installed. Then activate the environment. E.g. with `venv`:

```
python -m venv my_catalog_env
source my_catalog_env/bin/activate
```

### Step 2 - Clone the repo and install the package

Run the following from your command line:
```
git clone https://github.com/datalad/datalad-catalog.git
cd datalad-catalog
pip install -e .
```

Congratulations! You have now installed `datalad-catalog`.

#### Note on dependencies:

Because this is an extension to `datalad` and builds on metadata handling functionality, the installation process also installed [`datalad`](https://github.com/datalad/datalad) and [`datalad-metalad`](https://github.com/datalad/datalad-metalad) as dependencies, although these do not have to be used as the only sources of metadata for a catalog.

While the catalog generation process does not expect data to be structured as DataLad datasets, it can still be very useful to do so when building a full (meta)data management pipeline from raw data to catalog publishing. For complete instructions on how to install `datalad` and `git-annex`, please refer to the [DataLad Handbook](https://handbook.datalad.org/en/latest/intro/installation.html).

Similarly, the metadata input to `datalad-catalog` can come from any source as long as it conforms to the catalog schema. While the catalog does not expect metadata originating only from `datalad-metalad`'s extractors, this tool has advanced metadata handling capabilities that will integrate seamlessly with DataLad datasets and the catalog generation process.


## 4. Generating a catalog

The overall catalog generation process actually starts several steps before the involvement of `datalad-catalog`. Steps include:

1. curating data into datasets (a group of files in an hierarchical tree)
2. adding metadata to datasets and files (the process for this and the resulting metadata formats and content vary widely depending on domain, file types, data availability, and more)
3. extracting the metadata using an automated tool to output metadata items into a standardized and queryable set
4. in the current context: translating the metadata into the catalog schema
5. in the current context: using `datalad-catalog` to generate a catalog from the schema-conforming metadata

The first four steps in this list can follow any arbitrarily specified procedures and can use any arbitrarily specified tools to get the job done. If these steps are completed, correctly formatted data can be input, together with some configuration details, to `datalad-catalog`. This tool then provides several basic commands for catalog generation and customization. *For example:*

```bash

datalad catalog validate -m <path/to/input/data>
# Validate input data located at <path/to/input/data> according to the catalog's schema.

datalad catalog create -c <path/to/catalog/directory> -m <path/to/input/data>
# Create a catalog at location <path/to/catalog/directory>, using input data located at <path/to/input/data>.

datalad catalog add -c <path/to/catalog/directory> -m <path/to/input/data>
# Add metadata to an existing catalog at location <path/to/catalog/directory>, using input data located at <path/to/input/data>.

datalad catalog set-super -c <path/to/catalog/directory> -i <dataset_id> -v <dataset_version>
# Set the superdataset of an existing catalog at location <path/to/catalog/directory>, where the superdataset id and version are provided as arguments. The superdataset will be the first dataset displayed when navigating to the root URL of a catalog.

datalad catalog serve -c <path/to/catalog/directory>
# Serve the content of the catalog at location <path/to/catalog/directory> via a local HTTP server.

```

<div id="tutorial"><div>

## 5. Tutorial

To explore the basic functionality of `datalad-catalog`, please refer to [these tutorials](https://github.com/datalad/tutorials/tree/master/notebooks/catalog_tutorials#readme).


## 6. An example workflow

The DataLad ecosystem provides a complete set of free and open source tools that, together, provide full control over dataset/file access and distribution, version control, provenance tracking, metadata addition/extraction/aggregation, and catalog generation. 

DataLad itself can be used for decentralised management of data as lightweight, portable and extensible representations. DataLad MetaLad can extract structured high- and low-level metadata and associate it with these datasets or with individual files. And at the end of the workflow, DataLad Catalog can turn the structured metadata into a user-friendly data browser.

Importantly, DataLad Catalog can operate independently as well. Since it provides its own schema in a standard vocabulary, any metadata that conforms to this schema can be submitted to the tool in order to generate a catalog. Metadata items do not necessarily have to be derived from DataLad datasets, and the metadata extraction does not have to be conducted via DataLad MetaLad.

Even so, the provided set of tools can be particularly powerful when used together in a distributed (meta)data management pipeline.

<br>
<div style="text-align:center;">
    <img src="docs/source/_static/datacat3_the_toolset.svg" width="75%"></img>
</div>


## 7. Contributing

### Feedback / comments

Please [create a new issue](https://github.com/jsheunis/data-browser-from-metadata/issues/new) if you have any feedback, comments, or requests.

### Developer requirements

If you'd like to contribute as a developer, you need to install a number of extra dependencies:

```
cd datalad-catalog
pip install -r requirements-devel.txt
```

This installs `sphinx` and related packages for documentation building, `coverage` for code coverage, and `pytest` for testing.

### Contribution process

To make a contribution to the code or documentation, please:

- create an issue describing the bug/feature
- fork the project repository,
- create a branch from `main`,
- check that tests succeed: from the project root directory, run `pytest`
- commit your changes,
- push to your fork
- create a pull request with a clear description of the changes
## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://jsheunis.github.io/"><img src="https://avatars.githubusercontent.com/u/10141237?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Stephan Heunis</b></sub></a><br /><a href="https://github.com/datalad/datalad-catalog/issues?q=author%3Ajsheunis" title="Bug reports">🐛</a> <a href="https://github.com/datalad/datalad-catalog/commits?author=jsheunis" title="Code">💻</a> <a href="#content-jsheunis" title="Content">🖋</a> <a href="#data-jsheunis" title="Data">🔣</a> <a href="https://github.com/datalad/datalad-catalog/commits?author=jsheunis" title="Documentation">📖</a> <a href="#design-jsheunis" title="Design">🎨</a> <a href="#ideas-jsheunis" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-jsheunis" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-jsheunis" title="Maintenance">🚧</a> <a href="https://github.com/datalad/datalad-catalog/commits?author=jsheunis" title="Tests">⚠️</a> <a href="#question-jsheunis" title="Answering Questions">💬</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!