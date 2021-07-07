## --- UNDER DEVELOPMENT ---
---


# Data browser from structured DataLad-generated metadata

This is a single-page VueJS application that reads structured data from a local file (located at `metadata/dataset_obj.json`) and renders a somewhat standardized (meta)data browser interface from the structured data.

## To run this locally

### Step 1 - Clone the repo and checkout the `stephan-dev` branch

```
git clone https://github.com/jsheunis/data-browser-from-metadata.git
cd data-browser-from-metadata
git checkout stephan-dev
```

### Step 2 - Start a webserver with Python

This is necessary because the code uses [XMLHttpRequest](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest) to `GET` data from the local file, and you will run into CORS errors (e.g. [here](https://stackoverflow.com/questions/10752055/cross-origin-requests-are-only-supported-for-http-error-when-loading-a-local)) when trying to access content on the local file system without a web server.

With Python 3 run the following from the root directory of your cloned repo:

```
python3 -m http.server
```

This opens a server on [http://localhost:8000/](http://localhost:8000/) as standard, which you can navigate to in your browser.

### Step 3 - Open the `frontend.html` page

You can open it from the `localhost` page, or open [http://localhost:8000/frontend.html](http://localhost:8000/frontend.html) directly.


## Current status

The project is in early stages of development, so there will be inefficiencies and bugs and code that will be replaced in future.

The data object in the `metadata/dataset_obj.json` was constructed manually and does not (yet) conform fully to a known standard or structure. It also does not yet use a specific schema or vocabulary. The fields consist of a mixture of dummy/nonsensical data and actual data available online. Subdatasets and file hierarchies are currently built into the single data object using the `children` field. This works easily for small objects, but will break for large datasets. Currently investigating whether approaching this in a similar way as [datasets.datalad.org](https://datasets.datalad.org/) (i.e. reading the local directory structure from a separate metadata file located in each directory of the full hierarchy) will address concerns related to travesing large dataset trees.

The frontend interface currently allows:
- Viewing standard metadata fields for a dataset, such as name, description, DOI, keywords, and more.
- Links, suggestions and other interactions with the metadata (e.g. "Download with DataLad" and more).
- Browsing through subdirectories and files of said dataset, and viewing subdatasets in this hierarchy.
- Opening up subdatasets with the same view as for the top-level dataset, and with the same sub-level functionality.
- Browsing through funding information.

## Feedback / comments

Please [create a new issue](https://github.com/jsheunis/data-browser-from-metadata/issues/new) if you have any feedback, comments, or requests.










