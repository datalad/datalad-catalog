// Component definition: about
const aboutPage = () =>
  fetch(template_dir + "/about-template.html").
    then(response => {return response.text()}).
    then(text => {
      return {
        template: text,
        data: function () {
          return {
          };
        },
        methods: {
        },
      }
    })