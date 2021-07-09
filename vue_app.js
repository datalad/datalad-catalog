// Data
const metadata_dir = './metadata';
const json_file = metadata_dir + '/dataset_obj.json';

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
  },
  methods: {
    toggle: function() {
      if (this.isFolder) {
        this.isOpen = !this.isOpen;
      }
    }, 
    selectDataset(obj, objId) {
      this.$root.selectedDataset = obj;
      this.$root.dataPath.push(obj.short_name);
      
    },   
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
    }
  },
  beforeMount(){
    this.readTextFile(json_file)
  }
});