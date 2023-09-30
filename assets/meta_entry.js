/********/
// Data //
/********/
const default_config = {
  catalog_name: "DataCat",
  link_color: "#fba304",
  link_hover_color: "#af7714",
};

/**************/
// Components //
/**************/

/***********/
// Vue app //
/***********/

// Start Vue instance
var demo = new Vue({
  el: "#meta-entry",
  data: {
    metaTabIndex: {},
    dataset_name: "",
    dataset_description: "",
    logo_path: "artwork/catalog_logo.svg",
    form: {
      name: '',
      description: '',
      url: '',
      doi: '',
      dataset_id: '',
      dataset_version: '',
      keywords: [],
    },
    show: true
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
        mastodon: "https://fosstodon.org/@datalad",
        x: "https://x.com/datalad"
      };
      if (dest in destinations) {
        window.open(destinations[dest]);
      } else {
        window.open(dest);
      }
    },
    onSubmit(event) {
      event.preventDefault()
      downloadObjectAsJson(this.form, 'dataset_info.json')
      // alert(JSON.stringify(this.form))
    },
    onReset(event) {
      event.preventDefault()
      // Reset our form values
      this.form.name = '',
      this.form.description = '',
      this.form.url = '',
      this.form.doi = '',
      // Trick to reset/clear native browser form validation state
      this.show = false
      this.$nextTick(() => {
        this.show = true
      })
    }
  },
  beforeCreate() {
    // Set color scheme
    const style_text =
    ":root{--link-color: " +
    default_config.link_color +
    "; --link-hover-color: " +
    default_config.link_hover_color +
    ";}";
    const style_section = document.createElement("style");
    const node = document.createTextNode(style_text);
    style_section.appendChild(node);
    const body_element = document.getElementById("mainmetabody");
    body_element.insertBefore(style_section, body_element.firstChild);
    // Set logo
    // this.logo_path = default_config.logo_path;
  },
});

function downloadObjectAsJson(obj, filename){
  var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));
  var downloadAnchorNode = document.createElement('a');
  downloadAnchorNode.setAttribute("href",     dataStr);
  downloadAnchorNode.setAttribute("download", filename + ".json");
  document.body.appendChild(downloadAnchorNode);
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
}