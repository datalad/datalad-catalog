// JSON-LD data
const url = 'https://raw.githubusercontent.com/psychoinformatics-de/studyforrest-www/master/content/metadata/studyforrest.json';

// Component definition: recursive item in data tree
Vue.component("tree-item", {
  template: "#item-template",
  props: {
    item: [Object, Array, String],
    index: String
  },
  data: function() {
    return {
      isOpen: false
    };
  },
  computed: {
    isFolder: function() {
      return this.item instanceof Array || this.item instanceof Object
    },
    isObject: function() {
      return this.item instanceof Object
    },
    displayText: function() {
      if (this.item instanceof Array) {
        return this.$vnode.key + ' (array)'
      }
      else if (this.item instanceof Object) {
        if (this.item.hasOwnProperty('name')){
          return this.item["name"]
        }
        else if (this.item.hasOwnProperty('@id')){
          return this.item["@id"]
        }
        else {
          return this.$vnode.key
        }
      }
      else {
        return "|- " + this.$vnode.key + ": " + this.item
      }
    },
  },
  methods: {
    toggle: function() {
      if (this.isFolder) {
        this.isOpen = !this.isOpen;
      }
    },    
  }
});

// Fetch data, then start the Vue app
fetch(url)
.then((resp) => resp.json())
.then(function(data) {
  // Start Vue instance
  var demo = new Vue({
    el: "#demo",
    data: {
        studyData: data,
    }
  });
})
.catch(function(error) {
  console.log(error);
});