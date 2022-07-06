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

Since this site is self-contained and static, no further build processes, server-side implementations, or access to content delivery networks (CDNs) are necessary in order to serve the content. All that is needed is a simple HTTP server.

This can be achieved locally, for example using Python:

```bash
cd path/to/catalog/directory
python3 -m http.server
```

The content can also be hosted and served online. A straightforward and free way to achieve this is via GitHub and [GitHub Pages](https://pages.github.com/). After publishing this content as a GitHub repository, you can activate GitHub Pages in the repository's settings. See detailed instructions [here](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

## Maintaining content

Metadata entries can be updated, added to, and removed from the catalog in a decentralized and collaborative manner. Please refer to the [`datalad-catalog` documentation](http://docs.datalad.org/projects/catalog/en/latest/?badge=latest) for detailed instructions.

## Feedback, issues and contributions

Please log any feedback or problems you encounter with regards to the functioning of the catalog as an [issue](https://github.com/datalad/datalad-catalog/issues/new) on the `datalad-catalog` repository. For missing or unexpected metadata content, please contact the maintainer of this catalog.

Contributions to this open source project are welcome! Please refer to the [contributor guidelines](http://docs.datalad.org/projects/catalog/en/latest/contributing.html) for more information.

