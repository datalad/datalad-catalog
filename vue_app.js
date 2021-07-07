// JSON-LD data
const url = 'https://raw.githubusercontent.com/psychoinformatics-de/studyforrest-www/master/content/metadata/studyforrest.json';
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
      // this.selectedDataset = []
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
      
        // this.$root.dataPath.push(obj.short_name);
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



// // Component definition: recursive item in data tree v2
// Vue.component("tree-item-v2", {
//   template: "#item-template-v2",
//   props: {
//     item: [Object, Array, String, Number]
//   },
//   data: function() {
//     return {
//       isOpen: false
//     };
//   },
//   computed: {
//     isFolder: function() {
//       return this.item.hasOwnProperty('children')
//     },
//     x: function() {
//       return this.item instanceof Object
//     },
//     displayText: function() {
//       if (this.item instanceof Array) {
//         return this.$vnode.key + ' (array)'
//       }
//       else if (this.item instanceof Object) {
//         if (this.item.hasOwnProperty('name')){
//           return this.item["name"]
//         }
//         else if (this.item.hasOwnProperty('@id')){
//           return this.item["@id"]
//         }
//         else {
//           return this.$vnode.key
//         }
//       }
//       else {
//         return "|- " + this.$vnode.key + ": " + this.item
//       }
//     },
//   },
//   methods: {
//     toggle: function() {
//       if (this.isFolder) {
//         this.isOpen = !this.isOpen;
//       }
//     },    
//   }
// });