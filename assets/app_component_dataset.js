// Component definition: dataset view
const datasetView = () =>
  fetch(template_dir + "/dataset-template.html").
    then(response => {return response.text()}).
    then(text => {
      return {
        /* component definition */
        template: text,
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
              // Most recent metadata update
              sorted_metadata_sources = dataset.metadata_sources.sources.sort(
                (a, b) => b.source_time - a.source_time
              );
              disp_dataset.last_updated = this.getDateFromUTCseconds(
                sorted_metadata_sources[0].source_time
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
              disp_dataset.is_gin = false; // GIN
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
                    disp_dataset.url = disp_dataset.url.replace('git@github.com:', 'https://github.com');
                  }
                  if (dataset.url[i].toLowerCase().indexOf("gin.g-node") >= 0) {
                    disp_dataset.is_gin = true;
                    disp_dataset.url = dataset.url[i];
                    disp_dataset.url = disp_dataset.url.replace('git@gin.g-node.org:', 'https://gin.g-node.org');
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
              // Create href mailto for request access contact
              if (
                dataset.hasOwnProperty("access_request_contact") &&
                dataset["access_request_contact"]
              ) {
                var email_to = dataset.access_request_contact.email
                var email_subject = "Access request: " + disp_dataset.short_name

                disp_dataset.access_request_mailto =
                  "mailto:" + 
                  email_to +
                  "?subject=" +
                  email_subject +
                  "&body=Dear%20" +
                  dataset.access_request_contact.givenName +
                  "%20" + 
                  dataset.access_request_contact.familyName;
              }

              // Write main derived variable and set to ready
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
                  a.source_time > b.source_time ? 1 : -1
                );
              } else {
                sorted = subdatasets.sort((a, b) =>
                  a.source_time < b.source_time ? 1 : -1
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
                sorted_metadata_sources = subds_json[index].metadata_sources.sources.sort(
                  (a, b) => b.source_time - a.source_time
                );
                this.$root.selectedDataset.subdatasets[index].source_time =
                  sorted_metadata_sources[0].source_time;
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
                sorted_metadata_sources = subds_json[index].metadata_sources.sources.sort(
                  (a, b) => b.source_time - a.source_time
                );
                this.$root.selectedDataset.subdatasets[index].source_time =
                  sorted_metadata_sources[0].source_time;
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
        }
      }
    })