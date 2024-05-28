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
            showCopyDatasetAliasTooltip: false,
            showCopyDatasetIdTooltip: false,
            showCopyDatasetFullTooltip: false,
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
            citation_busy: false,
            citation_text: "",
            invalid_doi: false,
          };
        },
        watch: {
          subdatasets_ready: function (newVal, oldVal) {
            if (newVal) {
              console.debug("Watched property: subdatasets_ready = true")
              console.debug("Subdatasets have been fetched:");
              this.subdatasets = this.selectedDataset.subdatasets;
              console.debug(this.subdatasets);
              tags = this.tag_options;
              if (this.subdatasets) {
                this.subdatasets.forEach((subds, index) => {
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
            // The code in this function is executed once the properties,
            // children, variables, and everything related to the currently
            // selected dataset is deemed "ready". This means subdatasets
            // have been fetched and some subdataset properties have been
            // collected to assist dataset-level UX (including search tags)
            if (newVal) {
              console.debug("Watched property: dataset_ready = true")
              console.debug("Active dataset:");
              dataset = this.selectedDataset;
              console.debug(this.selectedDataset);
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
              disp_dataset["display_name"] = disp_dataset["short_name"];
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
              disp_dataset.last_updated = sorted_metadata_sources[0].source_time
              if (disp_dataset.last_updated) {
                disp_dataset.last_updated = this.getDateFromUTCseconds(
                  disp_dataset.last_updated
                );
              }
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
                    disp_dataset.url = disp_dataset.url.replace('ssh://', '');
                    disp_dataset.url = disp_dataset.url.replace('git@gin.g-node.org:', 'https://gin.g-node.org');
                    disp_dataset.url = disp_dataset.url.replace('git@gin.g-node.org', 'https://gin.g-node.org');
                    disp_dataset.url = disp_dataset.url.replace('.git', '');
                  }
                }
                if (!disp_dataset.url) {
                  disp_dataset.url = dataset.url[0];
                }
              } else {
                disp_dataset.url = dataset.url;
                if (disp_dataset.url && dataset.url.toLowerCase().indexOf("gin.g-node") >= 0) {
                  disp_dataset.is_gin = true;
                  disp_dataset.url = disp_dataset.url.replace('ssh://', '');
                  disp_dataset.url = disp_dataset.url.replace('git@gin.g-node.org:', 'https://gin.g-node.org');
                  disp_dataset.url = disp_dataset.url.replace('git@gin.g-node.org', 'https://gin.g-node.org');
                  disp_dataset.url = disp_dataset.url.replace('.git', '');
                }
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
              // Rendering options for dataset page
              if (this.$root.hasOwnProperty("dataset_options") && this.$root.dataset_options.hasOwnProperty("include_metadata_export")) {
                disp_dataset.show_export = this.$root.dataset_options.include_metadata_export
              }
              else {
                disp_dataset.show_export = false
              }
              // Determine show/hide confirg for "Request access" button
              if (dataset.config?.hasOwnProperty("dataset_options") && dataset.config.dataset_options.hasOwnProperty("include_access_request")) {
                disp_dataset.show_access_request = dataset.config.dataset_options.include_access_request
              }
              else {
                // default should be to display the access request button, if access request contact/url are included
                disp_dataset.show_access_request = true
              }
              // Show / hide binder button: if disp_dataset.url exists OR if dataset has a notebook specified in metadata
              disp_dataset.show_binder_button = false
              if ( disp_dataset.url || dataset.hasOwnProperty("notebooks") && dataset.notebooks.length > 0 ) {
                disp_dataset.show_binder_button = true
              }

              // Set correct URL query string to mirrorif keyword(s) included in query parameters
              if (this.$route.query.hasOwnProperty("keyword")) {
                query_keywords = this.$route.query.keyword
                // if included keywords(s) not null or empty string/array/object
                if (query_keywords) {
                  console.debug("Keywords in query parameter taken from vue route:")
                  console.debug(query_keywords)
                  // if included keywords(s) = array
                  if ((query_keywords instanceof Array || Array.isArray(query_keywords))
                    && query_keywords.length > 0) {
                      // add all search tags
                      for (const el of query_keywords) {
                        console.log(`adding to search tags: ${el}`)
                        this.addSearchTag(el)
                      }
                  } else {
                    this.addSearchTag(query_keywords)
                  }
                }
              }

              // Add json-ld data to head
              var scripttag = document.getElementById("structured-data")
              if (!scripttag) {
                scripttag = document.createElement("script");
                scripttag.setAttribute("type", "application/ld+json");
                scripttag.setAttribute("id", "structured-data");
                document.head.appendChild(scripttag);
              }
              keys_to_populate = [
                  "name", // Text
                  "description", // Text
                  "alternateName", // Text
                  "creator", //	Person or Organization
                  "citation", // Text or CreativeWork
                  "funder", // Person or Organization
                  "hasPart", // URL or Dataset
                  // "isPartOf", // URL or Dataset
                  "identifier", // URL, Text, or PropertyValue
                  // "isAccessibleForFree", // Boolean
                  "keywords", // Text
                  "license", // URL or CreativeWork
                  // "measurementTechnique", // Text or URL
                  "sameAs", // URL
                  // "spatialCoverage", // Text or Place
                  // "temporalCoverage", // Text
                  // "variableMeasured", // Text or PropertyValue
                  "version", // Text or Number
                  // "url", // URL
                  "includedInDataCatalog", // DataCatalog
                  // "distribution", // DataDownload
              ]
              obj = {
                  "@context": "https://schema.org/",
                  "@type": "Dataset",
              }
              for (var k=0; k<keys_to_populate.length; k++) {
                key = keys_to_populate[k]
                obj[key] = this.getRichData(key, dataset, disp_dataset)
              }

              scripttag.textContent = JSON.stringify(pruneObject(obj));

              dataset_id_path = getFilePath(this.selectedDataset.dataset_id)
              fetch(dataset_id_path, {cache: "no-cache"})
                .then((response) => {
                  if(response.status == 404) {
                    this.selectedDataset.has_id_path = false
                  } else {
                    this.selectedDataset.has_id_path = true 
                  }
                })
                .catch(error => {
                  // do nothing
                })
              // Write main derived variable and set to ready
              this.displayData = disp_dataset;
              this.display_ready = true;
              console.debug("Watched property function completed: dataset_ready = true")
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
                c.authors.some(
                  (f) =>
                  f.givenName && f.givenName.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0 
                ) ||
                c.authors.some(
                  (f) =>
                  f.familyName && f.familyName.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0 
                ) ||
                c.authors.some(
                  (f) =>
                  f.name && f.name.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0
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
          showBackButtonComp() {
            if (this.currentIsHome()) {
              return false
            } else {
              return true
            }
          },
        },
        methods: {
          newTabActivated(newTabIndex, prevTabIndex, bvEvent) {
            var tabs = this.selectedDataset.available_tabs
            console.debug(
              "%c> USER INPUT: new tab selected (%s)",
              "color: white; font-style: italic; background-color: blue",
              tabs[newTabIndex]
            );
            if (tabs[newTabIndex] == 'content') {
              this.getFiles()
            }
            // Update URL query string whenever a new tab is selected
            this.updateURLQueryString(this.$route, newTabIndex)
          },
          updateURLQueryString(current_route, tab_index = null) {
            // This function is called from:
            // - addSearchTag(): when adding a search tag (a.k.a. keyword) - WITHOUT tab_index param
            // - removeSearchTag(): when removing a search tag (a.k.a. keyword) - WITHOUT tab_index param
            // - newTabActivated(): when a new tab is selected or programmatically activated - WITH tab_index param
            console.debug("---\nUpdating URL query string\n---")
            console.debug("- Argument tab_index: %i", tab_index)
            console.debug("- Before: Vue Route query params: %s", JSON.stringify(Object.assign({}, current_route.query)))
            let url_qp = new URL(document.location.toString()).searchParams
            console.debug("- Before: URL query string: %s", url_qp.toString())
            var query_tab
            if (Number.isInteger(tab_index)) {
              query_tab = this.selectedDataset.available_tabs[tab_index];
            } else {
              default_tab = this.$root.selectedDataset.config?.dataset_options?.default_tab
              query_tab = url_qp.get("tab") ? url_qp.get("tab") : (default_tab ? default_tab : "content")
            }
            query_string = '?tab=' + query_tab
            if (this.search_tags.length > 0) {
              for (const element of this.search_tags) {
                query_string = query_string + '&keyword=' + element
              }
            }
            history.replaceState(
              {},
              null,
              current_route.path + query_string
            )
            console.debug("- After: Vue Route query params: %s", JSON.stringify(Object.assign({}, this.$route.query)))
            let url_qp2 = new URL(document.location.toString()).searchParams
            console.debug("- After: URL query string: %s", url_qp2.toString())
          },
          getRichData(key, selectedDS, displayDS) {
            switch (key) {
              case "name":
                return displayDS.display_name ? displayDS.display_name : ""
              case "description":
                return selectedDS.description ? selectedDS.description : ""
              case "alternateName":
                // use alias if present
                return [selectedDS.alias ? selectedDS.alias : ""]
              case "creator":
                // authors
                return selectedDS.authors?.map( (auth) => {
                  return {
                    "@type": "Person",
                    "givenName": auth.givenName ? auth.givenName : null,
                    "familyName": auth.familyName ? auth.familyName : null,
                    "name": auth.name ? auth.name : null,
                    "sameAs": this.getAuthorORCID(auth),
                  }
                })
              case "citation":
                // from publications
                return selectedDS.publications?.map( (pub) => {
                  return pub.doi
                })
              case "funder":
                // from funding
                return selectedDS.funding?.map( (fund) => {
                  var fund_obj = {
                    "@type": "Organization",
                    "name": fund.funder ? fund.funder : (fund.name ? fund.name : (fund.description ? fund.description : null)),
                  }
                  var sameas = this.getFunderSameAs(fund)
                  if (sameas) {
                    fund_obj["sameAs"] = sameas
                  }
                  return fund_obj
                })
              case "hasPart":
                // from subdatasets
                var parts = selectedDS.subdatasets?.map( (ds) => {
                  return {
                      "@type": "Dataset",
                      "name": ds.dirs_from_path[ds.dirs_from_path.length - 1]
                  }
                })
                return parts.length ? parts : null
              // case "isPartOf":
              case "identifier":
                // use DOI
                return selectedDS.doi ? selectedDS.doi : null
              // "isAccessibleForFree", // Boolean
              case "keywords":
                return selectedDS.keywords?.length ? selectedDS.keywords : null
              case "license":
                return selectedDS.license?.url ? selectedDS.license.url : null
              // "measurementTechnique", // Text or URL
              case "sameAs":
                // homepage
                if (selectedDS.additional_display && selectedDS.additional_display.length) {
                  for (var t=0; t<selectedDS.additional_display.length; t++) {
                    var current_display = selectedDS.additional_display[t]
                    var homepage = current_display.content?.homepage?.["@value"]
                    if (homepage) {
                      return homepage
                    }
                  }
                } else {
                  return null
                }
              // "spatialCoverage", // Text or Place
              // "temporalCoverage", // Text
              // "variableMeasured", // Text or PropertyValue
              case "version":
                return selectedDS.dataset_version
              // "url", // URL
              case "includedInDataCatalog":
                var obj = {
                  "@type":"DataCatalog",
                  "name": this.$root.catalog_config?.catalog_name ? this.$root.catalog_config.catalog_name : null,
                  "url": this.$root.catalog_config?.catalog_url ? this.$root.catalog_config.catalog_url : null,
                }
                if (obj.name == null && obj.url == null) {
                  return null
                } else {
                  return obj
                }
              // "distribution", // DataDownload
              default:
                return null
            }
          },
          getAuthorORCID(author) {
            if (author.hasOwnProperty("identifiers") && author.identifiers.length > 0) {
              orcid_element = author.identifiers.filter(
                (x) => x.name === "ORCID"
              );
              if (orcid_element.length > 0) {
                orcid_code = orcid_element[0].identifier
                const prefix = "https://orcid.org/"
                return orcid_code.indexOf(prefix) >= 0 ? orcid_code : prefix + orcid_code
              } else {
                return null
              }
            } else {
              return null
            }
          },
          getFunderSameAs(fund) {
            const common_funders = [
              {
                "name": "Deutsche Forschungsgemeinschaft",
                "alternate_name": "DFG",
                "ror": "https://ror.org/018mejw64"
              },
              {
                "name": "National Science Foundation",
                "alternate_name": "NSF",
                "ror": "https://ror.org/021nxhr62"
              }
            ]
            for (var i=0; i<common_funders.length; i++) {
              var cf = common_funders[i]
              if (fund.funder?.indexOf(cf.name) >= 0 ||
                  fund.name?.indexOf(cf.name) >= 0 ||
                  fund.description?.indexOf(cf.name) >= 0 ||
                  fund.funder?.indexOf(cf.alternate_name) >= 0 ||
                  fund.name?.indexOf(cf.alternate_name) >= 0 ||
                  fund.description?.indexOf(cf.alternate_name) >= 0 ) {
                return cf.ror
              }
            }
            return null
          },
          copyCloneCommand(index) {
            // https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative
            // https://www.sitepoint.com/clipboard-api/
            selectText = document.getElementById("clone_code").textContent;
            selectText = '\n      ' + selectText + '  \n\n  '
            selectText = selectText.replace(/^\s+|\s+$/g, '');
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
          copyDatasetURL(url_type) {
            // https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative
            // https://www.sitepoint.com/clipboard-api/
            urlmap = {
              'alias': "showCopyDatasetAliasTooltip",
              'id': "showCopyDatasetIdTooltip",
              'full': "showCopyDatasetFullTooltip",
            }
            selectText = document.getElementById(url_type + "_url").textContent;
            selectText = '\n      ' + selectText + '  \n\n  '
            selectText = selectText.replace(/^\s+|\s+$/g, '');
            navigator.clipboard
              .writeText(selectText)
              .then(() => {})
              .catch((error) => {
                alert(`Copy failed! ${error}`);
              });
            this[urlmap[url_type]] = true;
          },
          hideURLTooltipLater(url_type) {
            setTimeout(() => {
              urlmap = {
                'alias': "showCopyDatasetAliasTooltip",
                'id': "showCopyDatasetIdTooltip",
                'full': "showCopyDatasetFullTooltip",
              }
              this[urlmap[url_type]] = false;
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
          async selectDataset(event, obj, objId, objVersion, objPath) {
            console.debug(
              "%c> USER INPUT: dataset selected",
              "color: white; font-style: italic; background-color: blue",
            );
            console.debug("Inside selectDataset")
            console.debug(event)
            event.preventDefault()
            var newBrowserTab = event.ctrlKey || event.metaKey || (event.button == 1)
            if (obj != null) {
              objId = obj.dataset_id;
              objVersion = obj.dataset_version;
              objPath = obj.path;
            }
            file = getFilePath(objId, objVersion, objPath);
            fileExists = await checkFileExists(file);
            if (fileExists) {
              const route_info = {
                name: "dataset",
                params: {
                  dataset_id: objId,
                  dataset_version: objVersion,
                },
                query: {},
              }
              // before navigation, clear filtering options
              this.clearFilters()
              // now navigate
              if (newBrowserTab) {
                const routeData = router.resolve(route_info);
                console.log(routeData)
                window.open(routeData.href, '_blank');
              }
              else {
                this.search_tags = []
                // The following commented out code is an attempt to fix remaining
                // bugs with query strings that remain in the url when navigating to
                // a subdataset. This code tries to set the query string to null first,
                // by replacing the state, before pushing the next route via vue router.
                // It didn't seem to solve the issue, but should be investigated more.
                // history.replaceState(
                //   {},
                //   null,
                //   this.$route.path
                // )
                router.push(route_info);
              }
            } else {
              console.log(this.$root.subNotAvailable);
              this.$root.$emit("bv::show::modal", "modal-3", "#btnShow");
            }
          },
          clearFilters() {
            this.search_text = ""
            this.search_tags = []
            this.clearSearchTagText()
          },
          gotoHome() {
            console.debug(
              "%c> USER INPUT: home selected",
              "color: white; font-style: italic; background-color: blue",
            );
            // if there is NO home page set:
            // - if there is a tab name in the URL, navigate to current
            // - else: don't navigate, only "reset"
            // if there IS a home page set:
            // - if the current page IS the home page:
            //   - if there is a tab name in the URL, navigate to current
            //   - else: don't navigate, only "reset"
            // - if the current page is NOT the home page, navigate to home
            // reset: clear filters and set tab index = 0
            const current_route_info = {
              name: "dataset",
              params: {
                dataset_id: this.selectedDataset.dataset_id,
                dataset_version: this.selectedDataset.dataset_version,
              },
            }
            if (!this.catalogHasHome()) {
                this.clearFilters();
                this.tabIndex = this.getDefaultTabIdx();
                // Note: no need to call updateURLQueryString() here because a change to
                // this.tabIndex will automatically call newTabActivated() (because of
                // v-model="tabIndex"), which in turn calls updateURLQueryString().
            } else {
              if (this.currentIsHome()) {
                this.clearFilters();
                this.tabIndex = this.getDefaultTabIdx();
                // Note: no need to call updateURLQueryString() here because a change to
                // this.tabIndex will automatically call newTabActivated() (because of
                // v-model="tabIndex"), which in turn calls updateURLQueryString().
              } else {
                router.push({ name: "home" });
              }
            }            
          },
          catalogHasHome() {
            if (this.$root.home_dataset_id && this.$root.home_dataset_version) {
              return true
            } else {
              return false
            }
          },
          currentIsHome() {
            return ((this.$root.home_dataset_id == this.$root.selectedDataset.dataset_id) &&
            (this.$root.home_dataset_version == this.$root.selectedDataset.dataset_version))
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
          openWithBinder(dataset_url, current_dataset) {
            var environment_url =
              "https://mybinder.org/v2/gh/datalad/datalad-binder/main";
            var content_url = "https://github.com/jsheunis/datalad-notebooks";
            var content_repo_name = "datalad-notebooks";
            var notebook_name = "download_data_with_datalad_python.ipynb";
            var has_custom_notebook = false;
            if (current_dataset.hasOwnProperty("notebooks") && current_dataset.notebooks.length > 0) {
              // until including the functionality to select from multiple notebooks in a dropdown, just select the first one
              has_custom_notebook = true
              notebook = current_dataset.notebooks[0]
              content_url = notebook.git_repo_url.replace(".git", "")
              content_repo_name = content_url.substring(content_url.lastIndexOf('/') + 1)
              notebook_name = escapeHTML(notebook.notebook_path)
              if (notebook.hasOwnProperty("binder_env_url") && notebook["binder_env_url"]) {
                environment_url = notebook["binder_env_url"]
              }
            }

            binder_url =
              environment_url +
              "?urlpath=git-pull%3Frepo%3D" +
              content_url +
              "%26urlpath%3Dnotebooks%252F" +
              content_repo_name +
              "%252F" +
              notebook_name;

            if (!has_custom_notebook) {
              binder_url = binder_url +
                "%3Frepourl%3D%22" +
                dataset_url +
                "%22"
            }
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
            this.updateURLQueryString(this.$route)
          },
          removeSearchTag(tag) {
            idx = this.search_tags.indexOf(tag);
            if (idx > -1) {
              this.search_tags.splice(idx, 1);
            }
            this.filterTags();
            this.updateURLQueryString(this.$route)
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
            this.files_ready = false;
            this.$root.selectedDataset.tree = this.$root.selectedDataset["children"];
            this.files_ready = true;
          },
          async getNodeChildren() {
            this.files_ready = false;
            file_hash = this.selectedDataset.children;
            file = metadata_dir + "/" + file_hash + ".json";
            response = await fetch(file, {cache: "no-cache"});
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
                    // strip html tags from response text
                    let doc = new DOMParser().parseFromString(data, 'text/html');
                    this.selectedDataset.citation_text = doc.body.textContent || "";
                    this.citation_busy = false;
                  });
              } else {
                this.invalid_doi = true;
              }
            }
          },
          setCorrectTab(tab_param, available_tabs, default_tab) {
            // the set of available tabs have been updated in component
            // data in either created() or beforeRouteUpdate() and have been passed
            // as the second argument
            default_tab = default_tab ? default_tab : "content"
            var idx = available_tabs.indexOf(default_tab.toLowerCase())
            var default_tab_idx = idx >= 0 ? idx : 0

            // If no tab parameter is supplied via the router, set to default tab
            if (!tab_param) {
              this.tabIndex = default_tab_idx;
            }
            // If a tab parameter is supplied via the router, navigate to that tab if
            // part of available tabs, otherwise default tab
            else {
              tab_param = Array.isArray(tab_param) ? tab_param[0] : tab_param
              selectTab = available_tabs.indexOf(tab_param.toLowerCase())
              if (selectTab >= 0) {
                this.tabIndex = selectTab;
              } else {
                this.tabIndex = default_tab_idx;
              }
            }
          },
          getDefaultTabIdx() {
            var default_tab = this.selectedDataset.config?.dataset_options?.default_tab
            default_tab = default_tab ? default_tab : "content"
            var idx = this.selectedDataset.available_tabs.indexOf(default_tab.toLowerCase())
            return idx >= 0 ? idx : 0
          },
          clickBackButton() {
            console.debug(
              "%c> USER INPUT: backbutton clicked",
              "color: white; font-style: italic; background-color: blue",
            );
            history.back()
          },
        },
        async beforeRouteUpdate(to, from, next) {
          console.debug("Executing navigation guard: beforeRouteUpdate")
          this.subdatasets_ready = false;
          this.dataset_ready = false;
          file = getFilePath(to.params.dataset_id, to.params.dataset_version, null);
          response = await fetch(file, {cache: "no-cache"});
          text = await response.text();
          response_obj = JSON.parse(text);
          // if the object.type is redirect (i.e. the url parameter is an alias for or ID
          // of the dataset) replace the current route with one containing the actual id
          // and optionally version
          if (response_obj["type"] == "redirect") {
            route_params = {
              dataset_id: response_obj.dataset_id,
            }
            if (response_obj.dataset_version) {
              route_params.dataset_version = response_obj.dataset_version
            }
            const replace_route_info = {
              name: "dataset",
              params: route_params,
              query: to.query,
            }
            await router.replace(replace_route_info)
            return;
          }
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
            subdatasets_available = this.$root.selectedDataset.subdatasets.filter(
              (obj) => obj.available == "true"
            );
            subdatasets_unavailable = this.$root.selectedDataset.subdatasets.filter(
              (obj) => obj.available == "false"
            );
            this.$root.selectedDataset.subdatasets_count = this.$root.selectedDataset.subdatasets.length
            this.$root.selectedDataset.subdatasets_available_count = subdatasets_available.length
            this.$root.selectedDataset.subdatasets_unavailable_count = subdatasets_unavailable.length
            this.subdatasets_ready = true;
            this.$root.selectedDataset.has_subdatasets = true;
          } else {
            this.$root.selectedDataset.subdatasets = [];
            this.$root.selectedDataset.subdatasets_count = 0
            this.$root.selectedDataset.subdatasets_available_count = 0
            this.$root.selectedDataset.subdatasets_unavailable_count = 0
            this.subdatasets_ready = true;
            this.$root.selectedDataset.has_subdatasets = false;
          }
          // Now check file content
          this.files_ready = false;
          this.$root.selectedDataset.tree = this.$root.selectedDataset["children"];
          this.files_ready = true;
          if (
            this.$root.selectedDataset.hasOwnProperty("tree") &&
            this.$root.selectedDataset.tree instanceof Array &&
            this.$root.selectedDataset.tree.length > 0
          ) {
            this.$root.selectedDataset.has_files = true;
          }
          else {
            this.$root.selectedDataset.has_files = false;
          }
          // Now list all tabs and set the correct one
          // order in DOM: content, datasets, publications, funding, provenance,
          sDs = this.$root.selectedDataset
          available_tabs = ['content', 'datasets']
          standard_tabs = ['publications', 'funding', 'provenance']
          // add available standard tabs
          for (var t=0; t<standard_tabs.length; t++) {
            if (sDs[standard_tabs[t]] && sDs[standard_tabs[t]].length) {
              available_tabs.push(standard_tabs[t])
            }
          }
          // add available additional_display tabs
          if (sDs.additional_display && sDs.additional_display.length) {
            for (var t=0; t<sDs.additional_display.length; t++) {
              available_tabs.push(sDs.additional_display[t].name)
            }
          }
          // set the root data for available tabs
          available_tabs_lower = available_tabs
          this.$root.selectedDataset.available_tabs = available_tabs_lower
          // Now get dataset config if it exists
          dataset_config_path = metadata_dir + "/" + sDs.dataset_id + "/" + sDs.dataset_version + "/config.json";
          configresponse = await fetch(dataset_config_path, {cache: "no-cache"});
          if (configresponse.status == 404) {
            this.$root.selectedDataset.config = {};
          } else {
            configtext = await configresponse.text();
            config = JSON.parse(configtext);
            this.$root.selectedDataset.config = config;
          }
          // Set the correct tab to be rendered
          correct_tab = to.query.hasOwnProperty("tab") ? to.query.tab : null
          this.setCorrectTab(
            correct_tab,
            available_tabs_lower,
            this.$root.selectedDataset.config?.dataset_options?.default_tab
          )
          this.dataset_ready = true;
          console.debug("Finished navigation guard: beforeRouteUpdate")
          next();
        },
        async created() {
          this.dataset_ready = false;
          this.subdatasets_ready = false;
          console.debug("Executing lifecycle hook: created")
          // fetch superfile in order to set id and version on $root
          homefile = metadata_dir + "/super.json";
          homeresponse = await fetch(homefile, {cache: "no-cache"});
          if (homeresponse.status == 404) {
            this.$root.home_dataset_id = null;
            this.$root.home_dataset_version = null;
          } else {
            hometext = await homeresponse.text();
            homedataset = JSON.parse(hometext);
            this.$root.home_dataset_id = homedataset.dataset_id;
            this.$root.home_dataset_version = homedataset.dataset_version;
          }
          file = getFilePath(
            this.$route.params.dataset_id,
            this.$route.params.dataset_version,
            null
          );
          var app = this.$root;
          response = await fetch(file, {cache: "no-cache"});
          // Reroute to 404 if the dataset file is not found
          if (response.status == 404) {
            router.push({
              name: "404",
            });
            return;
          }
          text = await response.text();
          response_obj = JSON.parse(text);
          // if the object.type is redirect (i.e. the url parameter is an alias for or ID
          // of the dataset) replace the current route with one containing the actual id
          // and optionally version
          if (response_obj["type"] == "redirect") {
            route_params = {
              dataset_id: response_obj.dataset_id,
            }
            if (response_obj.dataset_version) {
              route_params.dataset_version = response_obj.dataset_version
            }
            const replace_route_info = {
              name: "dataset",
              params: route_params,
              query: this.$route.query,
            }
            await router.replace(replace_route_info)
            return;
          }
          app.selectedDataset = JSON.parse(text);
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
            subdatasets_available = this.$root.selectedDataset.subdatasets.filter(
              (obj) => obj.available == "true"
            );
            subdatasets_unavailable = this.$root.selectedDataset.subdatasets.filter(
              (obj) => obj.available == "false"
            );
            this.$root.selectedDataset.subdatasets_count = this.$root.selectedDataset.subdatasets.length
            this.$root.selectedDataset.subdatasets_available_count = subdatasets_available.length
            this.$root.selectedDataset.subdatasets_unavailable_count = subdatasets_unavailable.length
            this.subdatasets_ready = true;
            this.$root.selectedDataset.has_subdatasets = true;
          } else {
            this.$root.selectedDataset.subdatasets = [];
            this.$root.selectedDataset.subdatasets_count = 0
            this.$root.selectedDataset.subdatasets_available_count = 0
            this.$root.selectedDataset.subdatasets_unavailable_count = 0
            this.subdatasets_ready = true;
            this.$root.selectedDataset.has_subdatasets = false;
          }
          // Now check file content
          this.files_ready = false;
          this.$root.selectedDataset.tree = this.$root.selectedDataset["children"];
          this.files_ready = true;
          if (
            this.$root.selectedDataset.hasOwnProperty("tree") &&
            this.$root.selectedDataset.tree instanceof Array &&
            this.$root.selectedDataset.tree.length > 0
          ) {
            this.$root.selectedDataset.has_files = true;
          }
          else {
            this.$root.selectedDataset.has_files = false;
          }
          // Now list all tabs and set the correct one
          // order in DOM: content, datasets, publications, funding, provenance,
          sDs = this.$root.selectedDataset
          available_tabs = ['content', 'datasets']
          standard_tabs = ['publications', 'funding', 'provenance']
          // add available standard tabs
          for (var t=0; t<standard_tabs.length; t++) {
            if (sDs[standard_tabs[t]] && sDs[standard_tabs[t]].length) {
              available_tabs.push(standard_tabs[t])
            }
          }
          // add available additional_display tabs
          if (sDs.additional_display && sDs.additional_display.length) {
            for (var t=0; t<sDs.additional_display.length; t++) {
              available_tabs.push(sDs.additional_display[t].name)
            }
          }
          available_tabs_lower = available_tabs
          // set the root data for available tabs
          this.$root.selectedDataset.available_tabs = available_tabs_lower
          // Now get dataset config if it exists
          dataset_config_path = metadata_dir + "/" + sDs.dataset_id + "/" + sDs.dataset_version + "/config.json";
          configresponse = await fetch(dataset_config_path, {cache: "no-cache"});
          if (configresponse.status == 404) {
            this.$root.selectedDataset.config = {};
          } else {
            configtext = await configresponse.text();
            config = JSON.parse(configtext);
            this.$root.selectedDataset.config = config;
          }
          // ---
          // Note for future: Handle route query parameters (tab and keyword) here?
          // ---
          // This point in the code is reached from an explicit URL navigation to a dataset
          // (via home and/or via alias and/or via dataset-id, or directly to a dataset-version.
          // This means that explicit query parameters will be in the $route object.
          // (Note: when the same point is reached in the beforeRouteUpdate function,
          // it means that navigation happened from within the catalog (i.e. not explicitly / externally)
          // This means a new dataset page will be opened from the content tab or from the datasets tab of
          // the dataset that is being navigated away from. This means we do not want keyword or tab parameters to pass through.
          correct_tab = this.$route.query.hasOwnProperty("tab") ? this.$route.query.tab : null
          this.setCorrectTab(
            correct_tab,
            available_tabs_lower,
            this.$root.selectedDataset.config?.dataset_options?.default_tab
          )
          this.dataset_ready = true;
          console.debug("Finished lifecycle hook: created")
        },
        mounted() {
          console.debug("Executing lifecycle hook: mounted")
          this.tag_options_filtered = this.tag_options;
          this.tag_options_available = this.tag_options;
          console.debug("Finished lifecycle hook: mounted")
        }
      }
    })
