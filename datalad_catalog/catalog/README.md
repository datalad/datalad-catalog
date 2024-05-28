## The Catalog

This is a browsable data catalog generated from metadata using [`datalad-catalog`](https://github.com/datalad/datalad-catalog/). It is a self-contained and static [VueJS](https://vuejs.org/)-based site that can be viewed in any modern internet browser.

## Content

The content of this root directory includes everything necessary to serve the static site:

```
.
├── artwork
├── assets
├── config.json
├── index.html
├── metadata
└── README.md
```

The `artwork` and `assets` directories contain images and web assets (such as JavaScript and CSS files) respectively that support the rendering of the HTML components in `index.html`. The `config.json` file contains customizable configuration options supplied to `datalad-catalog`.

## Serving the content

Since this site is self-contained and static, no further build processes or access to content delivery networks (CDNs) are necessary in order to serve the content. All that is needed is a simple HTTP server with one specific addition - a custom redirect. This is required because the application makes use of [Vue Router's history mode](https://v3.router.vuejs.org/guide/essentials/history-mode.html#html5-history-mode), which requires a server-side redirect configuration to deal with the fact that a VueJS application is actually a single-page app.

For serving the content locally, this is already taken care of in `datalad-catalog`, and you can simply run the following:

```bash
cd path/to/catalog/directory
datalad catalog-serve -c .
```

The content can also be hosted and served online. A straightforward way to achieve this, and one which has a free tier, is via [Netlify](https://www.netlify.com/) (the common alternative, [GitHub Pages](https://pages.github.com/), does not currently support server-side redirects). After publishing this content, e.g. as a GitHub repository, you can link that repository to a site on Netlify. [See here](https://docs.netlify.com/routing/redirects/) how to set up redirects with Netlify. Of course, the site can also be served from your preferred server setup, as long as page redirects can be supported.

## Maintaining content

Metadata entries can be updated, added to, and removed from the catalog in a decentralized and collaborative manner. Please refer to the [`datalad-catalog` documentation](http://docs.datalad.org/projects/catalog/en/latest/?badge=latest) for detailed instructions.

## Feedback, issues and contributions

Please log any feedback or problems you encounter with regards to the functioning of the catalog as an [issue](https://github.com/datalad/datalad-catalog/issues/new) on the `datalad-catalog` repository. For missing or unexpected metadata content, please contact the maintainer of this catalog.

Contributions to this open source project are welcome! Please refer to the [contributor guidelines](http://docs.datalad.org/projects/catalog/en/latest/contributing.html) for more information.

