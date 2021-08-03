/*

BeforeMount: url refresh ==> check the path, push correct route

router.beforeEach: only when route changes ==> 

TODO: check if template can work per route. find correct way to pass data as props


*/



// Data
const metadata_dir = './metadata';
const web_dir = './web';
// const json_file = metadata_dir + '/dataset_obj.json';
const json_file = web_dir + '/ed946e96a98769a46c7cb92b89d071a9.json';



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


// Vue.component("page-not-found", {
//   template: "",
//   created: function() {
//       // Redirect outside the app using plain old javascript
//       window.location.href = "404.html";
//   }
// });


const datasetView = {
  template: "#dataset-template",
  props: {
    "selectedDataset": Object
  },
  data: function() {
    return {
      dataPath: [],
      showCopyTooltip: false,
    };
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
  }
};

// const datasetPage = {
//   template: "",
// };

const mainPage = {
  template: '<div><p>Main page</p></div>',
  props:['selectedDataset'],
};

const notFound = {
  template: '<img src="artwork/404.svg" class="d-inline-block align-middle" alt="404-not-found" style="width:70%;">',
  // created: function() {
  //     // Redirect outside the app using plain old javascript
  //     window.location.href = "404.html";
  // }
}

const routes = [
  { path: '/', component: mainPage, name: 'home' },
  { path: '/dataset/:blobId', component: datasetView, name: 'dataset' },
  { path: '*', component: notFound }
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
                console.log('FILE NOT FOUNDxxxx')
                alert('Dataset not foundxxxx')
              } else {

              }
          }
      }
      rawFile.open("GET", file, false);
      rawFile.send();
    
    }
  },
  beforeMount(){
    console.log('beforeMount')
    if(this.$route.params.hasOwnProperty('blobId')) {
      console.log('on refresh: dataset page')
      file = web_dir + '/' + this.$route.params.blobId + '.json'
    } else {
      console.log('on refresh: other page')
      file = json_file;
    }
    this.getJSONblob(file)

  },
  router
});

router.beforeEach((to, from, next) => {
  console.log('beforerouteupdateGLOBAL')
  if (to.name == 'dataset') {
    console.log('on reroute: dataset page')
    file = web_dir + '/' + to.params.blobId + '.json'
    // this.getJSONblob(file)
    var app = demo;
    var rawFile = new XMLHttpRequest(); // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
    rawFile.onreadystatechange = function () {
      if(rawFile.readyState === 4) {
          if(rawFile.status === 200 || rawFile.status == 0) {
              var allText = rawFile.responseText;
              app.easyDataFromFile = JSON.parse(allText);
              app.selectedDataset = app.easyDataFromFile;
          } else if (rawFile.status === 404) {
            console.log('FILE NOT FOUNDglobal')
            alert('Dataset not foundglobal')
          } else {

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
  // if (to.name !== 'Login' && !isAuthenticated) next({ name: 'Login' })
  // else next()
})