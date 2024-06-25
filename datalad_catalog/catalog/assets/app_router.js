/**********/
// Router //
/**********/

// Router routes definition
const routes = [
  {
    path: "/",
    name: "home",
    beforeEnter: (to, from, next) => {
      console.debug("Executing navigation guard: beforeEnter - route '/')")
      const superfile = metadata_dir + "/super.json";
      fetch(superfile, {cache: "no-cache"})
      .then((response) => {
        if(response.status == 404) {
          router.push({ name: "404" });
          next();
        }
        return response.text()
      }).then((text) => {
        superds = JSON.parse(text);
        router.push({
          name: "dataset",
          params: {
            dataset_id: superds["dataset_id"],
            dataset_version: superds["dataset_version"],
          },
          query: to.query,
        });
        next();
      })
      .catch(error => {
        console.error(error)
      })
    },
  },
  {
    path: "/dataset/:dataset_id/:dataset_version?",
    component: datasetView,
    name: "dataset",
  },
  { path: "/about", component: aboutPage, name: "about" },
  { 
    path: '/:catchAll(.*)', 
    component: notFound,
    name: '404'
  },
];

// Create router
const router = new VueRouter({
  mode: 'history',
  base: window.location.pathname.split('dataset/')[0],
  routes: routes,
  scrollBehavior(to, from, savedPosition) {
    return { x: 0, y: 0, behavior: "auto" };
  },
});