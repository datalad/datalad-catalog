/********/
// Data //
/********/
const config_file = "./config.json";
const metadata_dir = "./metadata";
const superdatasets_file = metadata_dir + "/super.json";
const json_file = metadata_dir + "/datasets.json";
const SPLIT_INDEX = 3;
const SHORT_NAME_LENGTH = 0; // number of characters in name to display, zero if all
const default_config = {
  catalog_name: "DataCat",
  link_color: "#fba304",
  link_hover_color: "#af7714",
  logo_path: "artwork/catalog_logo.svg",
};

/**************/
// Components //
/**************/

// Component definition: recursive item in data tree
Vue.component("tree-item", {
  template: "#item-template",
  props: {
    item: [Object, Array, String, Number],
  },
  data: function () {
    return {
      isOpen: false,
      files_ready: false,
      children: [],
    };
  },
  computed: {
    isFolder: function () {
      return this.item.type === "directory";
    },
    isDataset: function () {
      return this.item.type === "dataset";
    },
    displayText: function () {
      return this.item["name"];
    },
    byteText: function () {
      return this.formatBytes(this.item["contentbytesize"]);
    },
    downloadURL: function () {
      return this.getDownloadURL(this.item["url"]);
    },
  },
  methods: {
    async toggle() {
      if (this.isFolder) {
        tempIsOpen = !this.isOpen;
        if (tempIsOpen && !this.item.hasOwnProperty("children")) {
          obj = await this.getChildren(this.item);
          this.item.children = obj["children"];
          // go through all children, set state to enabled
          // then set disabled state for subdatasets that aren't part of catalog
          await Promise.all(
            this.item.children.map(async (child, index) => {
              child['state'] = 'enabled'
              if (child.type == "dataset") {
                file = getFilePath(child.dataset_id, child.dataset_version, "");
                fileExists = await checkFileExists(file);
                if (!fileExists) {
                  child['state'] = 'disabled'
                }
              }
            })
          );
          this.files_ready = true;
        }
        this.isOpen = !this.isOpen;
      }
    },
    async selectDataset(obj, objId, objVersion) {
      if (obj != null) {
        objId = obj.dataset_id;
        objVersion = obj.dataset_version;
      }
      // This check should not be necessary, because unavailable
      // subdatasets are already disabled, but the check is left here
      // to cover any other possible reasons for a file being unavailable
      file = getFilePath(objId, objVersion, "");
      fileExists = await checkFileExists(file);
      if (fileExists) {
        router.push({
          name: "dataset",
          params: {
            dataset_id: objId,
            dataset_version: objVersion,
          },
        });
      } else {
        console.log(this.$root.subNotAvailable);
        this.$root.$emit("bv::show::modal", "modal-3", "#btnShow");
      }
    },
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return "0 Bytes";
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
    },
    async getChildren(obj) {
      this.files_ready = false;
      // Grab ID and VERSION from currently active dataset.
      obj.dataset_id = this.$root.selectedDataset.dataset_id;
      obj.dataset_version = this.$root.selectedDataset.dataset_version;
      file = getFilePath(obj.dataset_id, obj.dataset_version, obj.path);
      try {
        response = await fetch(file);
        text = await response.text();
      } catch (error) {
        console.error(error);
      }
      return JSON.parse(text);
    },
    getDownloadURL(url_array) {
      if (url_array && url_array[0]) {
        return url_array[0];
      } else {
        return "";
      }
    },
  },
});

// Component definition: dataset view
const datasetView = {
  template: "#dataset-template",
  props: {
    selectedDataset: Object,
  },
  data: function () {
    return {
      dataPath: [],
      showCopyTooltip: false,
      showCopyCiteTooltip: false,
      tabIndex: 0,
      sort_name: true,
      sort_modified: true,
      sort_name_or_modified: true,
      search_text: "",
      search_tags: [],
      tag_text: "",
      tag_dropdown_open: false,
      tag_options: [],
      tag_options_filtered: [],
      tag_options_available: [],
      popoverShow: false,
      subdatasets: [],
      subdatasets_ready: false,
      dataset_ready: false,
      display_ready: false,
      displayData: {},
      files_ready: false,
      tags_ready: false,
      description_ready: false,
      description_display: "",
      citation_busy: false,
      citation_text: "",
      invalid_doi: false,
    };
  },
  watch: {
    subdatasets_ready: function (newVal, oldVal) {
      if (newVal) {
        console.log("subdatasets fetched!");
        this.subdatasets = this.selectedDataset.subdatasets;
        console.log("from watcher");
        console.log(this.subdatasets);
        tags = this.tag_options;
        if (this.subdatasets) {
          this.subdatasets.forEach((subds, index) => {
            console.log(index + "; " + subds);
            if (subds.available == "true" && subds.keywords) {
              tags = tags.concat(
                subds.keywords.filter((item) => tags.indexOf(item) < 0)
              );
            }
          });
        }
        this.tag_options = tags;
        this.tag_options_filtered = this.tag_options;
        this.tag_options_available = this.tag_options;
        this.tags_ready = true;
      }
    },
    dataset_ready: function (newVal, oldVal) {
      // TODO: some of these methods/steps should be moved to the generatpr tool. e.g. shortname
      if (newVal) {
        dataset = this.selectedDataset;
        console.log(this.selectedDataset);
        disp_dataset = {};
        // Set name to unknown if not available
        if (!dataset.hasOwnProperty("name") || !dataset["name"]) {
          disp_dataset["name"] = "<UNSPECIFIED>";
          disp_dataset["short_name"] = "<UNSPECIFIED>";
        } else {
          // Populate short_name
          if (!dataset.hasOwnProperty("short_name") || !dataset["short_name"]) {

            if (SHORT_NAME_LENGTH) {
              disp_dataset["short_name"] =
                dataset["name"].length > SHORT_NAME_LENGTH
                  ? dataset["name"].substring(0, SHORT_NAME_LENGTH) + "..."
                  : dataset["name"];
            }
            else {
              disp_dataset["short_name"] = dataset["name"];
            }
          } else {
            disp_dataset["short_name"] = dataset["short_name"];
          }
        }
        disp_dataset["display_name"] = " - " + disp_dataset["short_name"];
        // DOI
        if (!dataset.hasOwnProperty("doi") || !dataset["doi"]) {
          disp_dataset["doi"] = "not available";
        }
        // License
        if (
          !dataset.hasOwnProperty("license") ||
          !dataset["license"].hasOwnProperty("name") ||
          !dataset["license"]["name"]
        ) {
          disp_dataset["license"] = "not available";
        }
        // Latest extracted time
        sorted_extractors = dataset.extractors_used.sort(
          (a, b) => b.extraction_time - a.extraction_time
        );
        disp_dataset.metadata_extracted = this.getDateFromUTCseconds(
          sorted_extractors[0].extraction_time
        );
        // ID, version and location
        disp_dataset.file_path =
          "metadata/" +
          getRelativeFilePath(
            dataset.dataset_id,
            dataset.dataset_version,
            null
          );
        disp_dataset.id_and_version =
          dataset.dataset_id + "_" + dataset.dataset_version;
        disp_dataset.download_filename =
          "dataset_" + disp_dataset.id_and_version + ".json";
        // URL
        disp_dataset.is_github = false; // Github / gitlab / url / binder
        disp_dataset.is_gitlab = false; // Github / gitlab / url / binder
        disp_dataset.url = "";

        if (
          dataset.hasOwnProperty("url") &&
          (dataset["url"] instanceof Array || Array.isArray(dataset["url"])) &&
          dataset["url"].length > 0
        ) {
          for (var i = 0; i < dataset.url.length; i++) {
            if (dataset.url[i].toLowerCase().indexOf("github") >= 0) {
              disp_dataset.is_github = true;
              disp_dataset.url = dataset.url[i];
            }
          }
          if (!disp_dataset.url) {
            disp_dataset.url = dataset.url[0];
          }
        } else {
          disp_dataset.url = dataset.url;
        }

        // Description
        if (
          dataset.hasOwnProperty("description") &&
          (dataset["description"] instanceof Array ||
            Array.isArray(dataset["description"])) &&
          dataset["description"].length > 0
        ) {
          disp_dataset.description = dataset.description;
          disp_dataset.selected_description = disp_dataset.description[0];
          this.selectDescription(disp_dataset.selected_description);
        }
        if (
          (dataset.hasOwnProperty("description") &&
            dataset["description"] instanceof String) ||
          typeof dataset["description"] === "string"
        ) {
          this.description_ready = true;
        }
        this.displayData = disp_dataset;
        this.display_ready = true;
      }
    },
  },
  computed: {
    filteredSubdatasets() {
      all_subdatasets = this.subdatasets.filter(
        (obj) => obj.available == "true"
      );
      return all_subdatasets.filter((c) => {
        if (this.search_text == "") return true;
        return (
          c.dirs_from_path[c.dirs_from_path.length - 1]
            .toLowerCase()
            .indexOf(this.search_text.toLowerCase()) >= 0 ||
          // || (c.authors.some(e => e.givenName.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0))
          c.authors.some(
            (f) =>
              f.name.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0
          )
        );
      });
    },
    tagFilteredSubdatasets() {
      subdatasets = this.filteredSubdatasets;
      return subdatasets.filter((c) => {
        if (this.search_tags.length == 0) return true;
        return this.search_tags.every((v) => c.keywords ? c.keywords.includes(v): null);
      });
    },
    sortedSubdatasets() {
      subdatasets = this.tagFilteredSubdatasets;
      if (this.sort_name_or_modified) {
        if (this.sort_name) {
          sorted = subdatasets.sort((a, b) =>
            a.dirs_from_path[a.dirs_from_path.length - 1] >
            b.dirs_from_path[b.dirs_from_path.length - 1]
              ? 1
              : -1
          );
        } else {
          sorted = subdatasets.sort((a, b) =>
            a.dirs_from_path[a.dirs_from_path.length - 1] <
            b.dirs_from_path[b.dirs_from_path.length - 1]
              ? 1
              : -1
          );
        }
      } else {
        if (this.sort_modified) {
          sorted = subdatasets.sort((a, b) =>
            a.extraction_time > b.extraction_time ? 1 : -1
          );
        } else {
          sorted = subdatasets.sort((a, b) =>
            a.extraction_time < b.extraction_time ? 1 : -1
          );
        }
      }
      return sorted;
    },
  },
  methods: {
    copyCloneCommand(index) {
      // https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative
      // https://www.sitepoint.com/clipboard-api/
      selectText = document.getElementById("clone_code").textContent;
      navigator.clipboard
        .writeText(selectText)
        .then(() => {})
        .catch((error) => {
          alert(`Copy failed! ${error}`);
        });
      this.showCopyTooltip = true;
    },
    hideTooltipLater() {
      setTimeout(() => {
        this.showCopyTooltip = false;
      }, 1000);
    },
    copyCitationText(index) {
      // https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative
      // https://www.sitepoint.com/clipboard-api/
      selectText = document.getElementById("citation").textContent;
      navigator.clipboard
        .writeText(selectText)
        .then(() => {})
        .catch((error) => {
          alert(`Copy failed! ${error}`);
        });
      this.showCopyCiteTooltip = true;
    },
    hideCiteTooltipLater() {
      setTimeout(() => {
        this.showCopyCiteTooltip = false;
      }, 1000);
    },
    async selectDataset(obj, objId, objVersion, objPath) {
      if (obj != null) {
        objId = obj.dataset_id;
        objVersion = obj.dataset_version;
        objPath = obj.path;
      }
      file = getFilePath(objId, objVersion, objPath);
      fileExists = await checkFileExists(file);
      if (fileExists) {
        router.push({
          name: "dataset",
          params: {
            dataset_id: objId,
            dataset_version: objVersion,
          },
        });
      } else {
        console.log(this.$root.subNotAvailable);
        this.$root.$emit("bv::show::modal", "modal-3", "#btnShow");
      }
    },
    selectDescription(desc) {
      if (desc.content.startsWith("path:")) {
        this.description_ready = false;
        filepath = desc.content.split(":")[1];
        extension = "." + filepath.split(".")[1];
        desc_file = getFilePath(
          this.selectedDataset.dataset_id,
          this.selectedDataset.dataset_version,
          desc.path,
          extension
        );
        fetch(desc_file)
          .then((response) => response.blob())
          .then((blob) => blob.text())
          .then((markdown) => {
            this.description_display = marked.parse(markdown);
            this.description_ready = true;
          });
      } else {
        this.description_display = desc.content;
        this.description_ready = true;
      }
    },
    gotoHome() {
      router.push({ name: "home" });
    },
    getDateFromUTCseconds(utcSeconds) {
      // TODO: consider moving this functionality to generator tool
      var d = new Date(0); // epoch date
      d.setUTCSeconds(utcSeconds);
      day = d.getDate();
      month = d.getMonth() + 1; // getMonth() returns the month as a zero-based value
      year = d.getFullYear();
      return (
        year +
        "-" +
        (month > 9 ? month : "0" + month) +
        "-" +
        (day > 9 ? day : "0" + day)
      );
    },
    gotoURL(url) {
      window.open(url);
    },
    openWithBinder(dataset_url) {
      const environment_url =
        "https://mybinder.org/v2/gh/datalad/datalad-binder/parameter-test";
      const content_url = "https://github.com/jsheunis/datalad-notebooks";
      const content_repo_name = "datalad-notebooks";
      const notebook_name = "download_data_with_datalad_python.ipynb";
      binder_url =
        environment_url +
        "?urlpath=git-pull%3Frepo%3D" +
        content_url +
        "%26urlpath%3Dnotebooks%252F" +
        content_repo_name +
        "%252F" +
        notebook_name +
        "%3Frepourl%3D%22" +
        dataset_url +
        "%22";
      window.open(binder_url);
    },
    sortByName() {
      this.sort_name = !this.sort_name;
      this.sort_name_or_modified = true;
    },
    sortByModified() {
      this.sort_modified = !this.sort_modified;
      this.sort_name_or_modified = false;
    },
    toggleTagDropdown() {
      dd = this.$refs.tag_dropdown;
      if (!dd.shown) {
        dd.show();
      }
    },
    addSearchTag(option) {
      this.search_tags.push(option);
      this.clearSearchTagText();
      this.filterTags();
    },
    removeSearchTag(tag) {
      idx = this.search_tags.indexOf(tag);
      if (idx > -1) {
        this.search_tags.splice(idx, 1);
      }
      this.filterTags();
    },
    clearSearchTagText() {
      this.tag_text = "";
      this.filterTags();
      this.popoverShow = false;
    },
    filterTags() {
      this.tag_options_available = this.tag_options.filter(
        (x) => this.search_tags.indexOf(x) === -1
      );
      this.tag_options_filtered = this.tag_options_available.filter(
        (str) => str.toLowerCase().indexOf(this.tag_text.toLowerCase()) >= 0
      );
    },
    inputTagText() {
      this.popoverShow = true;
      this.filterTags();
    },
    onClose() {
      this.popoverShow = false;
    },
    validator(tag) {
      return this.tag_options_available.indexOf(tag) >= 0;
    },
    getFiles() {
      this.$root.selectedDataset.tree = this.$root.selectedDataset["children"];
      this.files_ready = true;
    },
    async getNodeChildren() {
      this.files_ready = false;
      file_hash = this.selectedDataset.children;
      file = metadata_dir + "/" + file_hash + ".json";
      response = await fetch(file);
      text = await response.text();
      obj = JSON.parse(text);
      this.$root.selectedDataset.tree = obj["children"];
      this.files_ready = true;
    },
    getCitationText(doi = "") {
      if (!this.selectedDataset.citation_text) {
        if (doi && doi.includes("https://doi.org/")) {
          this.invalid_doi = false;
          this.citation_busy = true;
          const headers = {
            Accept: "text/x-bibliography; style=apa",
          };
          fetch(doi, { headers })
            .then((response) => response.text())
            .then((data) => {
              this.selectedDataset.citation_text = data;
              console.log(data);
              this.citation_busy = false;
            });
        } else {
          this.invalid_doi = true;
        }
      }
    },
  },
  async beforeRouteUpdate(to, from, next) {
    if (this.tabIndex != 1) {
      this.tabIndex = 0;
    }
    this.subdatasets_ready = false;
    this.dataset_ready = false;

    file = getFilePath(to.params.dataset_id, to.params.dataset_version, null);
    response = await fetch(file);
    text = await response.text();
    this.$root.selectedDataset = JSON.parse(text);
    this.$root.selectedDataset.name = this.$root.selectedDataset.name
      ? this.$root.selectedDataset.name
      : "";
    this.$root.selectedDataset.short_name = this.$root.selectedDataset
      .short_name
      ? this.$root.selectedDataset.short_name
      : "";
    this.$root.selectedDataset.doi = this.$root.selectedDataset.doi
      ? this.$root.selectedDataset.doi
      : "";
    this.$root.selectedDataset.license = this.$root.selectedDataset.license
      ? this.$root.selectedDataset.license
      : {};
    this.$root.selectedDataset.authors = this.$root.selectedDataset.authors
      ? this.$root.selectedDataset.authors
      : [];
    this.$root.selectedDataset.keywords = this.$root.selectedDataset.keywords
      ? this.$root.selectedDataset.keywords
      : [];
    this.dataset_ready = true;

    if (
      this.$root.selectedDataset.hasOwnProperty("subdatasets") &&
      this.$root.selectedDataset.subdatasets instanceof Array &&
      this.$root.selectedDataset.subdatasets.length > 0
    ) {
      subds_json = await grabSubDatasets(this.$root);
      subds_json.forEach((subds, index) => {
        if (subds_json[index] != "unavailable") {
          sorted_extractors = subds_json[index].extractors_used.sort(
            (a, b) => b.extraction_time - a.extraction_time
          );
          this.$root.selectedDataset.subdatasets[index].extraction_time =
            sorted_extractors[0].extraction_time;
          this.$root.selectedDataset.subdatasets[index].name = subds_json[index]
            .name
            ? subds_json[index].name
            : "";
          this.$root.selectedDataset.subdatasets[index].short_name = subds_json[
            index
          ].short_name
            ? subds_json[index].short_name
            : "";
          this.$root.selectedDataset.subdatasets[index].doi = subds_json[index]
            .doi
            ? subds_json[index].doi
            : "";
          this.$root.selectedDataset.subdatasets[index].license = subds_json[
            index
          ].license
            ? subds_json[index].license
            : {};
          this.$root.selectedDataset.subdatasets[index].authors = subds_json[
            index
          ].authors
            ? subds_json[index].authors
            : [];
          this.$root.selectedDataset.subdatasets[index].keywords = subds_json[
            index
          ].keywords
            ? subds_json[index].keywords
            : [];
          this.$root.selectedDataset.subdatasets[index].available = "true";
        } else {
          this.$root.selectedDataset.subdatasets[index].available = "false";
        }
      });
      this.subdatasets_ready = true;
      console.log(this.subdatasets_ready);
    } else {
      this.$root.selectedDataset.subdatasets = [];
      this.subdatasets_ready = true;
    }
    next();
  },
  async created() {
    file = getFilePath(
      this.$route.params.dataset_id,
      this.$route.params.dataset_version,
      null
    );
    var app = this.$root;
    response = await fetch(file);
    text = await response.text();
    app.selectedDataset = JSON.parse(text);
    this.dataset_ready = true;
    if (
      this.$root.selectedDataset.hasOwnProperty("subdatasets") &&
      this.$root.selectedDataset.subdatasets instanceof Array &&
      this.$root.selectedDataset.subdatasets.length > 0
    ) {
      subds_json = await grabSubDatasets(app);
      subds_json.forEach((subds, index) => {
        if (subds_json[index] != "unavailable") {
          sorted_extractors = subds_json[index].extractors_used.sort(
            (a, b) => b.extraction_time - a.extraction_time
          );
          this.$root.selectedDataset.subdatasets[index].extraction_time =
            sorted_extractors[0].extraction_time;
          this.$root.selectedDataset.subdatasets[index].name =
            subds_json[index].name;
          this.$root.selectedDataset.subdatasets[index].short_name =
            subds_json[index].short_name;
          this.$root.selectedDataset.subdatasets[index].doi =
            subds_json[index].doi;
          this.$root.selectedDataset.subdatasets[index].license =
            subds_json[index].license;
          this.$root.selectedDataset.subdatasets[index].authors =
            subds_json[index].authors;
          this.$root.selectedDataset.subdatasets[index].keywords =
            subds_json[index].keywords;
          this.$root.selectedDataset.subdatasets[index].available = "true";
        } else {
          this.$root.selectedDataset.subdatasets[index].available = "false";
        }
      });
      this.subdatasets_ready = true;
    } else {
      this.$root.selectedDataset.subdatasets = [];
      this.subdatasets_ready = true;
    }
  },
  mounted() {
    this.tag_options_filtered = this.tag_options;
    this.tag_options_available = this.tag_options;
  },
};

// Component definition: main view
const mainPage = {
  template: "#main-template",
  data: function () {
    return {
      superdatasets: [],
    };
  },
  methods: {
    selectDataset(obj, objId, objVersion) {
      if (obj != null) {
        id_and_version = obj.dataset_id + "-" + obj.dataset_version;
      } else {
        id_and_version = objId + "-" + objVersion;
      }
      
      hash = md5(id_and_version);
      router.push({ name: "dataset", params: { blobId: hash } });
    },
    getSuperDatasets() {},
  },
};

// Component definition: 404 view
const notFound = {
  template:
    '<img src="artwork/404.svg" class="d-inline-block align-middle" alt="404-not-found" style="width:70%;">',
};

/**********/
// Router //
/**********/

// Router routes definition
const routes = [
  {
    path: "/",
    component: mainPage,
    name: "home",
    beforeEnter: (to, from, next) => {
      const superfile = metadata_dir + "/super.json";
      // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
      var rawFile = new XMLHttpRequest();
      rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4) {
          if (rawFile.status === 200 || rawFile.status == 0) {
            var allText = rawFile.responseText;
            superds = JSON.parse(allText);
            router.push({
              name: "dataset",
              params: {
                dataset_id: superds["dataset_id"],
                dataset_version: superds["dataset_version"],
              },
            });
            next();
          } else if (rawFile.status === 404) {
            router.push({ name: "404" });
          } else {
            // TODO: figure out what to do here
          }
        }
      };
      rawFile.open("GET", superfile, false);
      rawFile.send();
    },
  },
  {
    path: "/dataset/:dataset_id/:dataset_version",
    component: datasetView,
    name: "dataset",
  },
  { path: "/about", component: mainPage, name: "about" },
  { path: "*", component: notFound, name: "404" },
];

// Create router
const router = new VueRouter({
  routes: routes,
  scrollBehavior(to, from, savedPosition) {
    return { x: 0, y: 0, behavior: "auto" };
  },
});

/***********/
// Vue app //
/***********/

// Start Vue instance
var demo = new Vue({
  el: "#demo",
  data: {
    selectedDataset: {},
    logo_path: "",
  },
  methods: {
    gotoHome() {
      router.push({ name: "home" });
    },
    gotoAbout() {
      router.push({ name: "about" });
    },
    gotoExternal(dest) {
      const destinations = {
        github:
          "https://github.com/datalad/datalad-catalog",
        docs: "https://docs.datalad.org/projects/catalog/en/latest/",
        twitter: "https://twitter.com/datalad",
      };
      if (dest in destinations) {
        window.open(destinations[dest]);
      } else {
        window.open(dest);
      }
    },
  },
  beforeCreate() {
    fetch(config_file)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          console.log(
            "WARNING: config.json file could not be loaded; using defaults."
          );
          return default_config;
        }
      })
      .then((responseJson) => {
        obj = responseJson;
        // Set color scheme
        const style_text =
          ":root{--link-color: " +
          responseJson.link_color +
          "; --link-hover-color: " +
          responseJson.link_hover_color +
          ";}";
        const style_section = document.createElement("style");
        const node = document.createTextNode(style_text);
        style_section.appendChild(node);
        const body_element = document.getElementById("mainbody");
        body_element.insertBefore(style_section, body_element.firstChild);
        // Set logo
        if (obj.logo_path) {
          this.logo_path = obj.logo_path;
        } else {
          this.logo_path = default_config.logo_path;
        }
        // Settings for multiple property sources
      })
      .catch((error) => {
        console.log(error);
        this.logo_path = default_config.logo_path;
      });
  },
  router,
});

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
    // console.log(error);
    return false;
  }
}
