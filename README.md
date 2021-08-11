## --- UNDER DEVELOPMENT ---
---


# Data browser from structured DataLad-generated metadata

This code allows you to generate a standalone browser-based user interface for [Datalad](https://www.datalad.org/) datasets by: (1) parsing Datalad-derived metadata, (2) translating the metadata into structured data understandable and renderable by the frontend, and (3) generating a VueJS-based frontend with which to interactively browse the dataset's metadata.

## Online demo

Navigate to [https://jsheunis.github.io/data-browser-from-metadata/](https://jsheunis.github.io/data-browser-from-metadata/) to view a live demo of the current work-in-progress state of the user interface.

This demo site is hosted via GitHub Pages and it builds from the `stephan-dev` branch of this repo.

## How it works

DataLad's metadata capabilities (see [datalad-metalad](https://github.com/datalad/datalad-metalad)) allows one to extract metadata from DataLad datasets, subdatasets, and files, and to aggregate this information to the top-level dataset. When exported (using `datalad meta-dump`), these metadata objects can be ingested and parsed by the `webui_generate.py` script in this repo. This generator translates the DataLad metadata into structured data required by the VueJS-based user interface, and it also generates the assets for the interface (artwork, CSS, JavaScript and HTML). The resulting content can be hosted as a standalone website (as is the case for the demo above) without requiring any building steps beforehand.

## Run the interface locally

### Step 1 - Clone the repo and checkout the `stephan-dev` branch

```
git clone https://github.com/jsheunis/data-browser-from-metadata.git
cd data-browser-from-metadata
git checkout stephan-dev
```

### Step 2 - Start a webserver with Python

Ensure you have a recent version of Python installed, preferrably in a virtual environment.

The webserver is necessary because the code uses [XMLHttpRequest](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest) to `GET` data from local file, and you will run into CORS errors (e.g. [here](https://stackoverflow.com/questions/10752055/cross-origin-requests-are-only-supported-for-http-error-when-loading-a-local)) when trying to access content on the local file system without a web server.

With Python 3 run the following from the root directory of your cloned repo:

```
python3 -m http.server
```

### Step 3 - Open the locally hosted user interface

The step above opens a server at [http://localhost:8000/](http://localhost:8000/), which you can navigate to in your browser. This will render the `index.html` page in your browser, which is the same content that is served to the demo page.

For developers, this local server will allow you to view your changes in real-time as you develop. After making changes to `index.html`, `assets/vue_app.js` or `assets/style.css` (for example), you can refresh your browser tab to view changes.

## Run the generator locally

To run the complete process from "raw" metadata to user interface, you will need to run `webui_generate.py` with a list of DataLad-derived metadata objects as input. An example of such an input is provided in this repo at `data/studyforrest_metadata.json`, which is also the metadata from which the demo user interface was generated.

This JSON file contains a list of metadata objects that were generated as follows (these steps require some experience with DalaLad and its metadata functionality):

1. Clone the studyforrest dataset and subdatasets (https://github.com/psychoinformatics-de/studyforrest-data)
2. Add `studyminimeta.yaml` files to the top-level dataset and whichever subdatasets you'd like to see more information on.
3. Run metalad's `extract_metadata.py` on the studyforrest dataset. The command below recursively extracts metadata for files and subdatasets and aggregates and saves them all to the top-level dataset's metadata store:

```
python <path-to-datalad-metalad>/tools/extract_metadata.py -f metalad_core -r -a -s <path-to-studyforrest-data>
```
4. Export the metadata with `datalad meta-dump`
5. Save the exported metadata as a list of objects in a `.json` file.

To generate the complete user interface with required structured data, you can then run the following when located in your cloned `data-browser-from-metadata` repo:

```
python webui_generate.py data/studyforrest_metadata.json
```

This can of course also be run on your own file with DataLad-derived metadata.

Without the flag to specify an output directory (`-o <output-directory-location>`), `webui_generate.py` will save all outputs to the `_build` directory, where you can inspect the results.

To view your generated user interface, navigate to [http://localhost:8000/_build/](http://localhost:8000/_build/) (or alternatively to the relative path you specified with the `-o` flag).

## Current status

The project is in early stages of development, so there will be inefficiencies and bugs and code that will be replaced in future.

The frontend interface currently allows:
- A main page with a list of selectable superdatasets
- A dataset page that allows:
    - A unique ID (with navigable URL) for the specific dataset and version
    - Viewing standard metadata fields for a dataset, such as name, description, DOI, keywords, and more.
    - Links, suggestions and other interactions with the metadata (e.g. "Download with DataLad" and more).
    - A list of subdatasets of said dataset
    - Browsing through subdirectories and files of said dataset, and viewing subdatasets in this hierarchy.
    - Opening up subdatasets with the same view as for the top-level dataset, and with the same functionality.
    - Browsing through funding information and publications related to the dataset

The generator is also in need of improvement. Amongst other aspects, it does not currently take future operations such as dataset metadata deletion or ammendment into account, and will generate all outputs anew whenever it is run, overwriting existing content in the process.

Several TODO's are listed in `webui_generate.py` and `assets/vue_app.js`, including (informally worded):

- TODO: figure out logging
- TODO: figure out testing
- TODO: figure out installation / building process
- TODO: figure out automated updates to serving content somewhere
- TODO: figure out CI
- TODO: figure out what to do when a dataset belongs to multiple super-datasets
- TODO: if not provided, calculate directory/dataset size by accumulating children file sizes

## Feedback / comments

Please [create a new issue](https://github.com/jsheunis/data-browser-from-metadata/issues/new) if you have any feedback, comments, or requests.
