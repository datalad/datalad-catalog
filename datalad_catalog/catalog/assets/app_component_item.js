// Component definition: recursive item in data tree
Vue.component('tree-item', function (resolve, reject) {
  url = template_dir + "/item-template.html"
  fetch(url).
    then(response => {
        return response.text();
    }).
    then(text => {
        resolve(
          {
            template: text,
            props: {
              item: [Object, Array, String, Number],
            },
            data: function () {
              return {
                isOpen: false,
                files_ready: false,
                spinner_on: null,
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
                if (this.item["contentbytesize"]) {
                  return this.formatBytes(this.item["contentbytesize"]);
                } else {
                  return ""
                }
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
                    this.files_ready = false;
                    this.spinner_on = true;
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
                    this.spinner_on = false;
                  }
                  this.isOpen = !this.isOpen;
                }
              },
              async selectDataset(event, obj, objId, objVersion) {
                var newBrowserTab = event.ctrlKey || event.metaKey || (event.button == 1)
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
                  const route_info = {
                    name: "dataset",
                    params: {
                      dataset_id: objId,
                      dataset_version: objVersion,
                    },
                  }
                  // before navigation, clear filter options
                  this.$emit('clear-filters')
                  // now navigate
                  if (newBrowserTab) {
                    const routeData = router.resolve(route_info);
                    window.open(routeData.href, '_blank');
                  }
                  else {
                    router.push(route_info);
                  }
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
                if (url_array) {
                  if (Array.isArray(url_array)) {
                    return url_array[0];
                  } else {
                    return url_array;
                  }
                } else {
                  return "";
                }
              },
            }
          }
        )
    });
});