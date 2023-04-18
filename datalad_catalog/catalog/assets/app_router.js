/**********/
// Router //
/**********/

// Router routes definition
const routes = [
  {
    path: "/",
    name: "home",
    beforeEnter: (to, from, next) => {
      const superfile = metadata_dir + "/super.json";
      // https://www.dummies.com/programming/php/using-xmlhttprequest-class-properties/
      var rawFile = new XMLHttpRequest();
      rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4) {
          if (rawFile.status === 200 || rawFile.status == 0) {
            var allText = rawFile.responseText;
            superds = JSON.parse(allText);
            router.push({
              name: "dataset",
              params: {
                dataset_id: superds["dataset_id"],
                dataset_version: superds["dataset_version"],
              },
            });
            next();
          } else if (rawFile.status === 404) {
            router.push({ name: "404" });
          } else {
            // TODO: figure out what to do here
          }
        }
      };
      rawFile.open("GET", superfile, false);
      rawFile.send();
    },
  },
  {
    path: "/dataset/:dataset_id/:dataset_version/:tab_name?",
    component: datasetView,
    name: "dataset",
  },
  { path: "/about", component: aboutPage, name: "about" },
  { path: "*", component: notFound, name: "404" },
];

// Create router
const router = new VueRouter({
  routes: routes,
  scrollBehavior(to, from, savedPosition) {
    return { x: 0, y: 0, behavior: "auto" };
  },
});