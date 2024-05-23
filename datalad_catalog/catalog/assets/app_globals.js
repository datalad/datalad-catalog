/********/
// Data //
/********/

const template_dir = "/templates";
const config_file = "/config.json";
const metadata_dir = "/metadata";
const superdatasets_file = metadata_dir + "/super.json";
const SPLIT_INDEX = 3;
const SHORT_NAME_LENGTH = 0; // number of characters in name to display, zero if all
const default_config = {
  catalog_name: "DataCat Demo",
  catalog_url: "https://datalad-catalog.netlify.app/",
  link_color: "#fba304",
  link_hover_color: "#af7714",
  logo_path: "/artwork/catalog_logo.svg",
  social_links: {
    about: null,
    documentation: "https://docs.datalad.org/projects/catalog/en/latest/",
    github: "https://github.com/datalad/datalad-catalog",
    mastodon: "https://fosstodon.org/@datalad",
    x: "https://x.com/datalad"
  },
  dataset_options: {
    include_metadata_export: true,
  }
};

/*************/
// Functions //
/*************/

async function grabSubDatasets(app) {
  subds_json = [];
  await Promise.all(
    app.selectedDataset.subdatasets.map(async (subds, index) => {
      id_and_version = subds.dataset_id + "-" + subds.dataset_version;
      subds_file = getFilePath(subds.dataset_id, subds.dataset_version, null);
      try {
        subds_response = await fetch(subds_file, {cache: "no-cache"});
        subds_text = await subds_response.text();
      } catch (e) {
        console.error(e);
      } finally {
        try {
          subds_json[index] = JSON.parse(subds_text);
        } catch (er) {
          console.error(er);
          subds_json[index] = "unavailable";
        }
      }
    })
  );
  return subds_json;
}

function getFilePath(dataset_id, dataset_version, path, ext = ".json") {
  // Get node file location from  dataset id, dataset version, and node path
  // using a file system structure similar to RIA stores
  // - dataset_id is required, all the other parameters are optional
  // - dataset_id could either be an actual dataset ID or an alias
  file = metadata_dir + "/" + dataset_id
  blob = dataset_id
  if (dataset_version) {
    file = file + "/" + dataset_version;
    blob = blob + "-" + dataset_version;
    // path to file only makes sense with the context of a dataset id AND version
    if (path) {
      blob = blob + "-" + path;
    }
    blob = md5(blob);
    blob_parts = [blob.substring(0, SPLIT_INDEX), blob.substring(SPLIT_INDEX)];
    return file + "/" + blob_parts[0] + "/" + blob_parts[1] + ext;
  } else {
    blob = md5(blob);
    return file + "/" + blob + ext;
  }
}

function getRelativeFilePath(dataset_id, dataset_version, path) {
  // Get node file location from  dataset id, dataset version, and node path
  // (using a file system structure similar to RIA stores), relative to metadata
  // directory.
  file_path = dataset_id + "/" + dataset_version;
  blob = dataset_id + "-" + dataset_version;
  if (path) {
    blob = blob + "-" + path;
  }
  blob = md5(blob);
  blob_parts = [blob.substring(0, SPLIT_INDEX), blob.substring(SPLIT_INDEX)];
  file_path = file_path + "/" + blob_parts[0] + "/" + blob_parts[1] + ".json";
  return file_path;
}

async function checkFileExists(url) {
  try {
    const response = await fetch(url, {
      method: "HEAD",
      cache: "no-cache",
    });
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

function pruneObject(obj) {
  const newObj = {};
  Object.entries(obj).forEach(([k, v]) => {
    if (typeof v === 'object' && !Array.isArray(v) && v !== null) {
      newObj[k] = pruneObject(v);
    } else if ((v instanceof Array || Array.isArray(v)) && v.length > 0) {
      newArr = []
      for (const el of v) {
        if (typeof el === 'object' && !Array.isArray(el) && el !== null) {
          newArr.push(pruneObject(el))
        } else if (el != null) {
          newArr.push(el)
        }
      }
      newObj[k] = newArr;
    } else if (v != null) {
      newObj[k] = obj[k];
    }
  });
  return newObj;
}

