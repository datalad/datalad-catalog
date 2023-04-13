/********/
// Data //
/********/

const config_file = "./config.json";
const metadata_dir = "./metadata";
const superdatasets_file = metadata_dir + "./super.json";
const json_file = metadata_dir + "./datasets.json";
const SPLIT_INDEX = 3;
const SHORT_NAME_LENGTH = 0; // number of characters in name to display, zero if all
const default_config = {
  catalog_name: "DataCat",
  link_color: "#fba304",
  link_hover_color: "#af7714",
  logo_path: "artwork/catalog_logo.svg",
  social_links: {
    about: null,
    documentation: null,
    github: null,
    twitter: null,
  },
  dataset_options: {
    include_metadata_export: true,
  }
};
const template_dir = "./templates";

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
        subds_response = await fetch(subds_file);
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
        console.log(subds_json[index]);
      }
    })
  );
  return subds_json;
}

function getFilePath(dataset_id, dataset_version, path, ext = ".json") {
  // Get node file location from  dataset id, dataset version, and node path
  // using a file system structure similar to RIA stores
  file = metadata_dir + "/" + dataset_id + "/" + dataset_version;
  blob = dataset_id + "-" + dataset_version;
  if (path) {
    blob = blob + "-" + path;
  }
  blob = md5(blob);
  blob_parts = [blob.substring(0, SPLIT_INDEX), blob.substring(SPLIT_INDEX)];
  file = file + "/" + blob_parts[0] + "/" + blob_parts[1] + ext;
  return file;
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