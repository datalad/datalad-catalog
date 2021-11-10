/********/
// Data //
/********/
const metadata_dir = './metadata';
const superdatasets_file = metadata_dir + '/super.json';
const json_file = metadata_dir + '/datasets.json';


/**************/
// Components //
/**************/

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
      tag_options_filtered: [],
      tag_options_available: [],
      popoverShow: false,
      subdatasets_ready: false,
      dataset_ready: false
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
    validator(tag) {
      return this.tag_options_available.indexOf(tag) >= 0
    }
  },
  async beforeRouteUpdate(to, from, next) {
    this.tabIndex = 0;
    this.subdatasets_ready = false;
    file = metadata_dir + '/' + to.params.blobId + '.json'
    response = await fetch(file);
    text = await response.text();
    this.$root.selectedDataset = JSON.parse(text);
    this.dataset_ready = true;
    this.tag_options = this.$root.selectedDataset["subdataset_keywords"];

    if (this.$root.selectedDataset.hasOwnProperty("subdatasets")
        && this.$root.selectedDataset.subdatasets instanceof Array
        && this.$root.selectedDataset.subdatasets.length > 0) {
      
      subds_json = await grabSubDatasets(this.$root);
      subds_json.forEach(
        (subds, index) => {
          this.$root.selectedDataset.subdatasets[index].extraction_time = subds_json[index].extraction_time;
          this.$root.selectedDataset.subdatasets[index].name = subds_json[index].name;
          this.$root.selectedDataset.subdatasets[index].short_name = subds_json[index].short_name;
          this.$root.selectedDataset.subdatasets[index].doi = subds_json[index].doi;
          this.$root.selectedDataset.subdatasets[index].license = subds_json[index].license;
          this.$root.selectedDataset.subdatasets[index].authors = subds_json[index].authors;
          this.$root.selectedDataset.subdatasets[index].keywords = subds_json[index].keywords;
          this.$root.selectedDataset.subdatasets[index].dirs_from_path = subds_json[index].dirs_from_path;
        }
      );
      this.subdatasets_ready = true;
    }
    next();
  },
  async created () {
    file = metadata_dir + '/' + this.$route.params.blobId + '.json'
    var app = this.$root;
    response = await fetch(file);
    text = await response.text();
    app.selectedDataset = JSON.parse(text);
    this.dataset_ready = true;
    this.tag_options = app.selectedDataset["subdataset_keywords"];
    subds_json = await grabSubDatasets(app);
    subds_json.forEach(
      (subds, index) => {
        this.$root.selectedDataset.subdatasets[index].extraction_time = subds_json[index].extraction_time;
        this.$root.selectedDataset.subdatasets[index].name = subds_json[index].name;
        this.$root.selectedDataset.subdatasets[index].short_name = subds_json[index].short_name;
        this.$root.selectedDataset.subdatasets[index].doi = subds_json[index].doi;
        this.$root.selectedDataset.subdatasets[index].license = subds_json[index].license;
        this.$root.selectedDataset.subdatasets[index].authors = subds_json[index].authors;
        this.$root.selectedDataset.subdatasets[index].keywords = subds_json[index].keywords;
        this.$root.selectedDataset.subdatasets[index].dirs_from_path = subds_json[index].dirs_from_path;
      }
    );
    this.subdatasets_ready = true;
  },
  mounted() {
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
  methods: {
    selectDataset(obj, objId) {
      id_and_version = obj.dataset_id + '-' + obj.dataset_version;
      hash = md5(id_and_version);
      router.push({ name: 'dataset', params: { blobId: hash } })
    },
    getSuperDatasets() {
      
    }
  },
};

// Component definition: 404 view
const notFound = {
  template: '<img src="artwork/404.svg" class="d-inline-block align-middle" alt="404-not-found" style="width:70%;">',
}


/**********/
// Router //
/**********/

// Router routes definition
const routes = [
  { path: '/', component: mainPage, name: 'home',
    beforeEnter: (to, from, next) => {
      const superfile = metadata_dir + '/super.json';
      var rawFile = new XMLHttpRequest(); // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
      rawFile.onreadystatechange = function () {
        if(rawFile.readyState === 4) {
            if(rawFile.status === 200 || rawFile.status == 0) {
                var allText = rawFile.responseText;
                superds = JSON.parse(allText);
                super_id_and_version = superds["dataset_id"] + '-' + superds["dataset_version"];
                hash = md5(super_id_and_version);
                router.push({ name: 'dataset', params: { blobId: hash } })
                next();
            } else if (rawFile.status === 404) {
              router.push({ name: '404'})
            } else {
              // TODO: figure out what to do here
            }
        }
      }
      rawFile.open("GET", superfile, false);
      rawFile.send();
    }
  },
  { path: '/dataset/:blobId', component: datasetView, name: 'dataset'},
  { path: '/about', component: mainPage, name: 'about'},
  { path: '*', component: notFound, name: '404'}
];

// Create router
const router = new VueRouter({
  routes: routes,
  scrollBehavior (to, from, savedPosition) {
    return { x: 0, y: 0, behavior: 'auto' };
  }
});


/***********/
// Vue app //
/***********/

// Start Vue instance
var demo = new Vue({
  el: "#demo",
  data: {
      selectedDataset: {},
  },
  methods: {
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
  router
});


/*************/
// Functions //
/*************/

async function grabSubDatasets(app) {
  subds_json = [];
  await Promise.all(app.selectedDataset.subdatasets.map(async (subds, index) => {
    id_and_version = subds.dataset_id + '-' + subds.dataset_version;
    hash = md5(id_and_version);
    subds_file = metadata_dir + '/' + hash + '.json';
    subds_response = await fetch(subds_file);
    subds_text = await subds_response.text();
    subds_json[index] = JSON.parse(subds_text);
  }));
  return subds_json
}


/*

TODO: use emit!!
TODO: add object and logic to track existence and content of dataset fields and resulting action (visibility, text to display, etc). E.g.:
-- if there are no publications, hide empty publication card and show sentence "There are currently no publications associated with this dataset."
-- show/hide components based on whether fields exist or are empty in json blob
-- populate filler/adapted text (e.g. time of extraction ==> utc seconds converted to display date)
*/