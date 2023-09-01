# 0.2.1 (Tue Mar 7, 2023) -- fix extension tests

### 🏠 Internal

- Start using a `maint` branch for releases

### 🛡 Tests

- Don't install `jq` dependency on Windows, don't collect and run workflow tests on windows. Issue [#256](https://github.com/datalad/datalad-catalog/issues/256), Commit [25dd1e7](https://github.com/datalad/datalad-catalog/commit/25dd1e7a8076579b025c55aeebe3c9f33083c5a2) (by [@jsheunis](https://github.com/jsheunis))

### 🪓 Deprecations and removals

- fix ModuleNotFoundError because of upstream metadata updates. Commit [649e941](https://github.com/datalad/datalad-catalog/commit/649e9415e297608f8a9d5adafea16c887eb9cc08) (by [@jsheunis](https://github.com/jsheunis))

### Authors: 1

- Stephan Heunis (@jsheunis)


# 0.2.0 (Thu Nov 24, 2022) -- jsonschema rendering + metadata forms + cleanup


### 🐛 Bug Fixes

- Fix keyword search malfunction to reset list correctly after keyword select. PR [#202](https://github.com/datalad/datalad-catalog/pull/202) (by [@jsheunis](https://github.com/jsheunis))


### 💫 Enhancements and new features

- UX: Make dataset page keyword search case insensitive. PR [#202](https://github.com/datalad/datalad-catalog/pull/202) (by [@jsheunis](https://github.com/jsheunis))
- UX: Make subdataset tags clickable. PR [#202](https://github.com/datalad/datalad-catalog/pull/202) (by [@jsheunis](https://github.com/jsheunis))
- UX: Improve handling and display of unavailable subdatasets in dataset page file browser. PR [#205](https://github.com/datalad/datalad-catalog/pull/205) (by [@jsheunis](https://github.com/jsheunis))
- UX: Display 'View on GIN' button for gin-hosted datasets, format ssh URLs as https to allow in-browser linking. PR [#228](https://github.com/datalad/datalad-catalog/pull/228) (by [@jsheunis](https://github.com/jsheunis))
- Schema: Add icon field to additional display property in dataset schema, which allows users to specify an icon that they want to be displayed in the additional tab. PR [#207](https://github.com/datalad/datalad-catalog/pull/207) (by [@jsheunis](https://github.com/jsheunis))
- Schema: Render a human-readable json schema definition + resolve local schemas via `$ref` and `$id` properties (see: https://datalad.github.io/datalad-catalog/display_schema.html). PR [#216](https://github.com/datalad/datalad-catalog/pull/216) + PR [#217](https://github.com/datalad/datalad-catalog/pull/217) (by [@jsheunis](https://github.com/jsheunis))
- Schema: Automatically render form from schema (currently disabled). PR [#225](https://github.com/datalad/datalad-catalog/pull/225) (by [@jsheunis](https://github.com/jsheunis))
- Schema: Add titles to all object properties in schemas. PR [#231](https://github.com/datalad/datalad-catalog/pull/231) (by [@jsheunis](https://github.com/jsheunis))
- Adds simplistic demo for metadata entry (see: https://datalad.github.io/datalad-catalog/metadata-entry.html). PR [#210](https://github.com/datalad/datalad-catalog/pull/210) (by [@jsheunis](https://github.com/jsheunis))

### 📝 Documentation

- Include info on workflow functionality in README. PR [#202](https://github.com/datalad/datalad-catalog/pull/202) (by [@jsheunis](https://github.com/jsheunis))
- Fix README typo. PR [#209](https://github.com/datalad/datalad-catalog/pull/209) (by [@Remi-Gau](https://github.com/Remi-Gau))
- Add information about the human-readable jsonschema of the catalog to docs. PR [#218](https://github.com/datalad/datalad-catalog/pull/218) (by [@jsheunis](https://github.com/jsheunis))
- Update README badges. PR [#227](https://github.com/datalad/datalad-catalog/pull/227) (by [@jsheunis](https://github.com/jsheunis))
- Remove unused pages from docs. PR [#227](https://github.com/datalad/datalad-catalog/pull/227) (by [@jsheunis](https://github.com/jsheunis), [@loj](https://github.com/loj))

### 🛡 Tests

- Enable CI on appveyor for pull requests and pushes to the `main` branch, and re-enable crippled filesystem test workflow with gh-actions. PR [#213](https://github.com/datalad/datalad-catalog/pull/213) + PR [#223](https://github.com/datalad/datalad-catalog/pull/223) (by [@jsheunis](https://github.com/jsheunis), [@yarikoptic](https://github.com/yarikoptic), [@mih](https://github.com/mih))

### 🪓 Deprecations and removals

- Remove unused mermaid dependency. PR [#203](https://github.com/datalad/datalad-catalog/pull/203) (by [@jsheunis](https://github.com/jsheunis))

### 🏠 Internal

- Substantial refactoring of html and javascript code of the Vue application, splitting up distinct JS functionality into separate files, and moving Vue component templates into separate files with async loading. PR [#215](https://github.com/datalad/datalad-catalog/pull/215) (by [@jsheunis](https://github.com/jsheunis))

### Authors:

- Laura Waite (@loj)
- Michael Hanke (@mih)
- Remi Gau (@Remi-Gau)
- Stephan Heunis (@jsheunis)
- Yaroslav Halchenko (@yarikoptic)

---

# 0.1.2 (Fri Sept 16 2022) -- red tests

#### 🛡 Tests
- Adds test data to package_data to ensure availability when installing from pip with extras [#199](https://github.com/datalad/datalad-catalog/pull/199) (by @jsheunis)

#### Authors: 1

- Stephan Heunis (@jsheunis)

---

# 0.1.1 (Tue Sept 13 2022) -- release continued

#### 💫 Enhancements and new features
- Adds automated workflow for PyPI release. [#197](https://github.com/datalad/datalad-catalog/pull/197) (by @jsheunis)

#### 📝 Documentation
- Adds CHANGELOG. [#197](https://github.com/datalad/datalad-catalog/pull/197) (by @jsheunis)

#### 🛡 Tests
- Updates appveyor setup to run tests with `pytest` [#197](https://github.com/datalad/datalad-catalog/pull/197) (by @jsheunis)

#### Authors: 1

- Stephan Heunis (@jsheunis)

---

# 0.1.0 (Tue Sept 13 2022) -- INITIAL RELEASE

#### 💫 Enhancements and new features
- First release of the `datalad-catalog` package on PyPI

#### Authors: 
- Adina Wagner (@adswa)
- Alex Waite (@aqw)
- Benjamin Poldrack (@bpoldrack)
- Christian Mönch (@christian-monch)
- Julian Kosciessa (@jkosciessa)
- Laura Waite (@loj)
- Leonardo Muller-Rodriguez (@Manukapp)
- Michael Hanke (@mih)
- Michał Szczepanik (@mslw)
- Stephan Heunis (@jsheunis)
- Yaroslav Halchenko (@yarikoptic)

<!-- EXAMPLE -->

<!-- # 0.1.1 (Tue Sept 13 2022) -- release continued

#### 💫 Enhancements and new features
- Something is now better than before, e.g. `test`. [#pr](pr-url) (by @jsheunis)

#### 🪓 Deprecations and removals

#### 🐛 Bug Fixes

#### 📝 Documentation

#### 🏠 Internal

#### 🛡 Tests

#### Authors: 1

- Stephan Heunis (@jsheunis) -->
