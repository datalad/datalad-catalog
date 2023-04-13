/***********/
// Vue app //
/***********/

// Start Vue instance
var datacat = new Vue({
  el: "#datacat",
  data: {
    selectedDataset: {},
    logo_path: "",
    links: {},
    dataset_options: {},
    config_ready: false,
  },
  methods: {
    gotoHome() {
      router.push({ name: "home" });
    },
    gotoAbout() {
      router.push({ name: "about" });
    },
    gotoExternal(dest) {
      window.open(dest);
    },
    async load() {
      // Load templates
      await Promise.all(
        Object.keys(template_paths).map(async (key, index) => {
          url = template_dir + "/" + template_paths[key]
          fetch(url).
          then(response => {
              return response.text();
          }).
          then(text => {
              console.log('template loaded: '+key)
              console.log(text)
              document.getElementById(key).innerHTML = text;
          });
        })
      )
    }
  },
  beforeCreate() {
    fetch(config_file)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          console.log(
            "WARNING: config.json file could not be loaded; using defaults."
          );
          return default_config;
        }
      })
      .then((responseJson) => {
        obj = responseJson;
        // set social links
        this.social_links = obj.social_links
        // set dataset options
        this.dataset_options = obj.dataset_options
        // Set color scheme
        const style_text =
          ":root{--link-color: " +
          responseJson.link_color +
          "; --link-hover-color: " +
          responseJson.link_hover_color +
          ";}";
        const style_section = document.createElement("style");
        const node = document.createTextNode(style_text);
        style_section.appendChild(node);
        const body_element = document.getElementById("mainbody");
        body_element.insertBefore(style_section, body_element.firstChild);
        // Set logo
        if (obj.logo_path) {
          this.logo_path = obj.logo_path;
        } else {
          this.logo_path = default_config.logo_path;
        }
        // Settings for multiple property sources
        this.config_ready = true
      })
      .catch((error) => {
        console.log("Config file error:");
        console.log(error);
        this.logo_path = default_config.logo_path;
      });
  },
  router,
});