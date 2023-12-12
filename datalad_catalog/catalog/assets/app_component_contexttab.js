// Component definition: an "additional tab" with context
Vue.component('context-tab-body', function (resolve, reject) {
  url = template_dir + "/context-tab-template.html"
  fetch(url).
    then(response => {
        return response.text();
    }).
    then(text => {
        resolve(
          {
            template: text,
            props: {
              tabby: Object,
            },
            data: function () {
              return {
                context_tab_ready: false,
              };
            },
            computed: {},
            methods: {
              toUpperString(str_in) {
                return str_in.charAt(0).toUpperCase() + str_in.slice(1)
              }
            },
            async created() {
              this.context_tab_ready = true;
              // console.log(new_tab)
            }
          }
        )
    });
});