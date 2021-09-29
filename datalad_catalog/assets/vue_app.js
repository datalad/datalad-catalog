/*

TODO: use emit!!
TODO: remove redundant methods from components / vue app instance
TODO: add object and logic to track existence and content of dataset fields and resulting action (visibility, text to display, etc). E.g.:
-- if there are no publications, hide empty publication card and show sentence "There are currently no publications associated with this dataset."
-- show/hide components based on whether fields exist or are empty in json blob
-- populate filler/adapted text (e.g. time of extraction ==> utc seconds converted to display date)
TODO: FOR CURRENT UPDATE:
  - go through html and js and see where there are redundant calls/sets to selectedDataset
  - find alternatives for ".some()" since it might not work in all browsers
  - sort out main page, "home", breadcrums, navigation and display
*/

// Data
const metadata_dir = './metadata';
const web_dir = './web';
const superdatasets_file = metadata_dir + '/datasets.json';
const json_file = metadata_dir + '/datasets.json';
// const super_dataset_id = 'deabeb9b-7a37-4062-a1e0-8fcef7909609';
// const super_dataset_version = '0321dbde969d2f5d6b533e35b5c5c51ac0b15758';
// const super_id_and_version = super_dataset_id + '-' + super_dataset_version;
// const super_hash = md5(super_id_and_version);

// Component definition: recursive item in data tree
Vue.component("tree-item", {
  template: "#item-template",
  props: {
    item: [Object, Array, String, Number]
  },
  data: function() {
    return {
      isOpen: false
    };
  },
  computed: {
    isFolder: function() {
      return this.item.children && this.item.children.length && this.item.type !== 'dataset';
    },
    isDataset: function() {
      return this.item.type === 'dataset'
    },
    displayText: function() {
      return this.item["name"]
    },
    byteText: function(){
      return this.formatBytes(this.item["contentbytesize"])
    }
  },
  methods: {
    toggle: function() {
      if (this.isFolder) {
        this.isOpen = !this.isOpen;
      }
    },
    selectDataset(obj, objId) {
      // this.$root.selectedDataset = obj;
      // this.$root.dataPath.push(obj.short_name);
      id_and_version = obj.dataset_id + '-' + obj.dataset_version;
      hash = md5(id_and_version);
      router.push({ name: 'dataset', params: { blobId: hash } })
    },
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
  }
});

// Component definition: dataset view
const datasetView = {
  template: "#dataset-template",
  props: {
    "selectedDataset": Object
  },
  data: function() {
    return {
      dataPath: [],
      showCopyTooltip: false,
      tabIndex: 0,
      sort_name: true,
      sort_modified: true,
      sort_name_or_modified: true,
      search_text: '',
      search_tags: [],
      tag_text: '',
      tag_dropdown_open: false,
      tag_options: [],
      // tag_options: [
      //   "human",
      //   "fMRI",
      //   "task",
      //   "7T",
      //   "3T",
      //   "audio",
      //   "visual",
      //   "music",
      //   "retinotopy",
      //   "angiography",
      //   "T1,T2",
      //   "stephan"
      // ],
      tag_options_filtered: [],
      tag_options_available: [],
      popoverShow: false
    };
  },
  computed: {
    displayData: function () {
      // TODO: some of these methods/steps should be moved to the generatpr tool. e.g. shortname
      dataset = this.selectedDataset;
      disp_dataset = {};
      // Populate short_name
      if (!dataset.hasOwnProperty("short_name") || !dataset["short_name"]) {
        disp_dataset["short_name"] = (dataset["name"].length > 30 ? dataset["name"].substring(0,30)+'...' : dataset["name"])
      } else {
        disp_dataset["short_name"] = dataset["short_name"]
      }
      // Display breadcrums and dataset name
      if (dataset.hasOwnProperty("root_dataset_id")) {
        disp_dataset["display_name"] = ' / ' + dataset["dataset_path"].replace('/', ' / ');
        disp_dataset["root_dataset"] = false;
        // this.dataPath.push(dataset.short_name);
      } else {
        disp_dataset["display_name"] = ' - ' + dataset["short_name"]
        disp_dataset["root_dataset"] = true;
      }
      // DOI
      if (!dataset.hasOwnProperty("doi") || !dataset["doi"]) {
        disp_dataset["doi"] = "not available"
      }
      // License
      if (!dataset.hasOwnProperty("license") || !dataset["license"].hasOwnProperty("name") || !dataset["license"]["name"]) {
        disp_dataset["license"] = "not available"
      }

      disp_dataset.metadata_extracted = this.getDateFromUTCseconds(dataset.extraction_time);
      id_and_version = dataset.dataset_id + '-' + dataset.dataset_version;
      disp_dataset.hash = md5(id_and_version);
      return disp_dataset
    },
    filteredSubdatasets() {
      subdatasets = this.selectedDataset.subdatasets;
      return subdatasets.filter(c => {
        if(this.search_text == '') return true;
        return ( (c.dirs_from_path[c.dirs_from_path.length - 1].toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0)
                  || (c.authors.some(e => e.givenName.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0)) 
                  || (c.authors.some(f => f.familyName.toLowerCase().indexOf(this.search_text.toLowerCase()) >= 0)) );
      })
    },
    tagFilteredSubdatasets() {
      // target.every(v => arr.includes(v));
      subdatasets = this.filteredSubdatasets;
      return subdatasets.filter(c => {
        if(this.search_tags.length == 0) return true;
        return ( this.search_tags.every(v => c.keywords.includes(v)) );
      })
    },
    sortedSubdatasets() {
      subdatasets = this.tagFilteredSubdatasets;
      if (this.sort_name_or_modified) {
        if (this.sort_name) {
          sorted = subdatasets.sort((a,b) => (a.dirs_from_path[a.dirs_from_path.length - 1] > b.dirs_from_path[b.dirs_from_path.length - 1] ? 1 : -1))
        } else {
          sorted = subdatasets.sort((a,b) => (a.dirs_from_path[a.dirs_from_path.length - 1] < b.dirs_from_path[b.dirs_from_path.length - 1] ? 1 : -1))
        }
      } else {
        if (this.sort_modified) {
          sorted = subdatasets.sort((a,b) => (a.extraction_time > b.extraction_time ? 1 : -1))
        } else {
          sorted = subdatasets.sort((a,b) => (a.extraction_time < b.extraction_time ? 1 : -1))
        }
      }
      return sorted
    },
  },
  methods: {
    copyCloneCommand(index) {
      // https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative
      // https://www.sitepoint.com/clipboard-api/
      selectText = document.getElementById("clone_code").textContent;
      navigator.clipboard.writeText(selectText)
        .then(() => { })
        .catch((error) => { alert(`Copy failed! ${error}`) })
        this.showCopyTooltip = true;
    },
    hideTooltipLater() {
      setTimeout(() => {
        this.showCopyTooltip = false;
      }, 1000);
    },
    selectDataset(obj, objId) {
      // this.$root.selectedDataset = obj;
      // this.$root.dataPath.push(obj.short_name);
      id_and_version = obj.dataset_id + '-' + obj.dataset_version;
      hash = md5(id_and_version);
      router.push({ name: 'dataset', params: { blobId: hash } })
    },
    gotoHome() {
      router.push({ name: 'home'})
    },
    getDateFromUTCseconds(utcSeconds) {
      // TODO: consider moving this functionality to generator tool
      var d = new Date(0); // epoch date
      d.setUTCSeconds(utcSeconds);
      day = d.getDate();
      month = d.getMonth();
      year = d.getFullYear();
      return year + '-' + (month > 9 ? month : '0' + month) + '-' + (day > 9 ? day : '0' + day)
    },
    gotoURL(url) {
      window.open(url);
    },
    openWithBinder(dataset_url) {
      const environment_url = 'https://mybinder.org/v2/gh/datalad/datalad-binder/parameter-test';
      const content_url = 'https://github.com/jsheunis/datalad-notebooks';
      const content_repo_name = 'datalad-notebooks';
      const notebook_name = 'download_data_with_datalad_python.ipynb';
      binder_url = environment_url + '?urlpath=git-pull%3Frepo%3D' + content_url + '%26urlpath%3Dnotebooks%252F' 
      + content_repo_name + '%252F' + notebook_name + '%3Frepourl%3D%22' + dataset_url + '%22';
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
      dd = this.$refs.tag_dropdown
      if (!dd.shown) {
        dd.show()
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
      this.tag_text = '';
      this.filterTags();
      this.popoverShow = false

    },
    filterTags() {
      this.tag_options_available = this.tag_options.filter(x => this.search_tags.indexOf(x)===-1);
      this.tag_options_filtered  = this.tag_options_available.filter(str => str.indexOf(this.tag_text) >= 0);
    },
    inputTagText() {
      this.popoverShow = true;
      this.filterTags();
    },
    onClose() {
      this.popoverShow = false
    },
    onShow() {
      // This is called just before the popover is shown
      // Reset our popover form variables
      // this.focusRef(this.$refs.tag_search_input)
    },
    onShown() {
      // Called just after the popover has been shown
      // Transfer focus to the first input
      
    },
    onHidden() {
      // Called just after the popover has finished hiding
      // this.tag_text = '';
      // Bring focus back to the button
      // this.focusRef(this.$refs.button)
    },
    focusRef(ref) {
      // Some references may be a component, functional component, or plain element
      // This handles that check before focusing, assuming a `focus()` method exists
      // We do this in a double `$nextTick()` to ensure components have
      // updated & popover positioned first
      this.$nextTick(() => {
        this.$nextTick(() => {
          ;(ref.$el || ref).focus()
        })
      })
    },
    validator(tag) {
      return this.tag_options_available.indexOf(tag) >= 0
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.tabIndex = 0;
    next();
  },
  mounted() {
    this.tag_options = this.selectedDataset["subdataset_keywords"]
    this.tag_options_filtered = this.tag_options;
    this.tag_options_available = this.tag_options;
  }
};

// Component definition: main view
const mainPage = {
  template: "#main-template",
  data: function() {
    return {
      superdatasets: []
    };
  },
  created: function () {
    comp = this;
    var rawFile = new XMLHttpRequest(); // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
      rawFile.onreadystatechange = function () {
          if(rawFile.readyState === 4) {
              if(rawFile.status === 200 || rawFile.status == 0) {
                  var allText = rawFile.responseText;
                  comp.superdatasets = JSON.parse(allText);
                  console.log("created and fetched")
                  console.log(JSON.parse(allText))
                  // console.log(this.superdatasets[0].dataset_version)
              } else if (rawFile.status === 404) {
                router.push({ name: '404'})
              } else {
                // TODO: figure out what to do here
              }
          }
      }
      rawFile.open("GET", superdatasets_file, false);
      rawFile.send();
  },
  methods: {
    selectDataset(obj, objId) {
      id_and_version = obj.dataset_id + '-' + obj.dataset_version;
      hash = md5(id_and_version);
      router.push({ name: 'dataset', params: { blobId: hash } })
    },
    getSuperDatasets() {
      
    }
  }
};

// Component definition: 404 view
const notFound = {
  template: '<img src="artwork/404.svg" class="d-inline-block align-middle" alt="404-not-found" style="width:70%;">',
}

// Router definition
const routes = [
  { path: '/', component: mainPage, name: 'home', redirect: to => ({
                                                    name: "dataset",
                                                    params: { blobId: getSuper() },
                                                  }),
  },
  // { path: '/', component: mainPage, name: 'home'},
  { path: '/dataset/:blobId', component: datasetView, name: 'dataset' },
  { path: '/about', component: mainPage, name: 'about' },
  { path: '*', component: notFound, name: '404' }
];
const router = new VueRouter({
  routes: routes,
  scrollBehavior (to, from, savedPosition) {
    return { x: 0, y: 0, behavior: 'auto' };
  }
});

// Start Vue instance
var demo = new Vue({
  el: "#demo",
  data: {
      // studyData: data,
      datasets: [1,2,3],
      selectedDataset: [],
      easyDataFromFile: [],
      dataPath: [],
      showCopyTooltip: false,
      dataFile: json_file,
  },
  methods: {
    copyCloneCommand(index) {
      // https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative
      // https://www.sitepoint.com/clipboard-api/
      selectText = document.getElementById("clone_code").textContent;
      navigator.clipboard.writeText(selectText)
        .then(() => { })
        .catch((error) => { alert(`Copy failed! ${error}`) })
        this.showCopyTooltip = true;
    },
    hideTooltipLater() {
      setTimeout(() => {
        this.showCopyTooltip = false;
      }, 1000);
    },
    readTextFile(file) {
      var app = this;
      var rawFile = new XMLHttpRequest();
      rawFile.onreadystatechange = function () {
          if(rawFile.readyState === 4) {
              if(rawFile.status === 200 || rawFile.status == 0) {
                  var allText = rawFile.responseText;
                  app.easyDataFromFile = JSON.parse(allText);
                  app.selectedDataset = app.easyDataFromFile;
              }
          }
      }
      rawFile.open("GET", file, false);
      rawFile.send();
    },
    getJSONblob(file) {
      var app = this;
      var rawFile = new XMLHttpRequest(); // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
      rawFile.onreadystatechange = function () {
          if(rawFile.readyState === 4) {
              if(rawFile.status === 200 || rawFile.status == 0) {
                  var allText = rawFile.responseText;
                  app.easyDataFromFile = JSON.parse(allText);
                  app.selectedDataset = app.easyDataFromFile;
              } else if (rawFile.status === 404) {
                router.push({ name: '404'})
              } else {
                // TODO: figure out what to do here
              }
          }
      }
      rawFile.open("GET", file, false);
      rawFile.send();
    },
    gotoHome() {
      router.push({ name: 'home'})
    },
    gotoAbout() {
      router.push({ name: 'about'})
    },
    gotoExternal(dest) {
      const destinations = {
        "github": "https://github.com/jsheunis/data-browser-from-metadata/tree/packaging",
        "docs": "https://github.com/jsheunis/data-browser-from-metadata/tree/packaging",
        "twitter": "https://twitter.com/datalad",
      }
      if (dest in destinations) {
        window.open(destinations[dest]);
      }
      else {
        window.open(dest);
      }
    }
  },
  beforeMount(){
    console.log('beforeMount')
    if(this.$route.params.hasOwnProperty('blobId')) {
      console.log('on refresh: dataset page')
      file = metadata_dir + '/' + this.$route.params.blobId + '.json'
    } else {
      console.log('on refresh: other page')
      file = json_file;
    }
    this.getJSONblob(file)
  },
  router
});

// Router function to run before each navigation
router.beforeEach((to, from, next) => {
  console.log('beforerouteupdateGLOBAL')
  if (to.name == 'dataset') {
    console.log('on reroute: dataset page')
    file = metadata_dir + '/' + to.params.blobId + '.json'
    var app = demo;
    var rawFile = new XMLHttpRequest(); // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
    rawFile.onreadystatechange = function () {
      if(rawFile.readyState === 4) {
          if(rawFile.status === 200 || rawFile.status == 0) {
              var allText = rawFile.responseText;
              app.easyDataFromFile = JSON.parse(allText);
              app.selectedDataset = app.easyDataFromFile;
          } else if (rawFile.status === 404) {
            router.push({ name: '404'})
          } else {
            // TODO: figure out what to do here
          }
      }
    }
    rawFile.open("GET", file, false);
    rawFile.send();
    next();
  }
  else { 
    console.log('on reroute: other page')
    next();
  }
});

function getSuper() {
  const superfile = metadata_dir + '/super.json';
  var rawFile = new XMLHttpRequest(); // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
  rawFile.onreadystatechange = function () {
    if(rawFile.readyState === 4) {
        if(rawFile.status === 200 || rawFile.status == 0) {
            var allText = rawFile.responseText;
            superds = JSON.parse(allText);
            super_id_and_version = superds["dataset_id"] + '-' + superds["dataset_version"];
            return md5(super_id_and_version); 
        } else if (rawFile.status === 404) {
          // router.push({ name: '404'})
        } else {
          // TODO: figure out what to do here
        }
    }
  }
  rawFile.open("GET", superfile, false);
  rawFile.send();
}