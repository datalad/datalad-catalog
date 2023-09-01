# 1.0.0 (Fri Sept 1 2023) -- Brand new CLI!

### Summary

This is the first major release update since the initial release,
mainly due to breaking changes in the command line interface.

Most of the changes were included in https://github.com/datalad/datalad-catalog/pull/309,
summarised as:
- update API to entrypoint per command: `create`, `add`, `validate`, `serve`, `get`, `set`, `remove`, `translate`, `workflow`
- introduce `datalad-next` dependency, at first for constraint system but in future for whatever functionality is useful
- refactor most of the code related to the main commands

Some of the important changes to take note of:

- Validation is now done according to the schema of a specific catalog (now located at `path-to-catalog/schema/*`), where previously validation was always done according to the latest schema of the installed package version (which is now the fallback).
- Metadata can be passed to any catalog command that takes it as in argument, in different formats: json lines from STDIN, JSON-serialized string, and a file with JSON lines.
- pytest fixtures are now located in `tests/fixtures.py` and exposed to all tests
- `catalog-get|set` provides an extensible set of commands for configuring a catalog and reporting its properties
- the handling of config files is refactored:
   - The main changes relate to how/when a config file is provided.
   - Previously, config files were specified during instantiation of the WebCatalog class, and a whole lot of obscure code was necessary to determine how this config applies to the catalog or dataset level.
   - The refactored code receives the config file via the Create() and Add() commands or via the WebCatalog.create() or Node.add_attributes() python methods.
   - Now, WebCatalog can be instantiated with location alone (no 'action'  necessary anymore, and no config_file)
   - Now, config is set on WebCatalog or Node instances after/during  running their respective create() methods and not during instantiation
- Translation functionality is refactored, and *requires updated to existing translators*:
   - With the new catalog argument, translation occurs to the specific schema version of the catalog (if  supported by an available translator); if the catalog argument is not supplied, the expected schema version is the latest supported by the package installation.
   - The translator matching process is streamlined by keeping track of previously matched and instantiated translators
   - Functionality to get the supported schema version, source name, and source version have been moved to the translator base class in order to support the abovementioned changes. This means existing and new translators will have to override these functions.


### 💫 Enhancements and new features
- Something is now better than before, e.g. `test`. [#pr](pr-url) (by @jsheunis)

- ENH: add a "request access" button for a dataset. PR [#235](https://github.com/datalad/datalad-catalog/pull/235) (by [@jsheunis](https://github.com/jsheunis))
- NF: Adds metadata translation functionality in dedicated class. PR [#246](https://github.com/datalad/datalad-catalog/pull/246) (by [@jsheunis](https://github.com/jsheunis))
- ENH: don't install jq dependency on windows. PR [#248](https://github.com/datalad/datalad-catalog/pull/248) (by [@jsheunis](https://github.com/jsheunis))
- ENH: refactoring config, extractors_used. PR [#237](https://github.com/datalad/datalad-catalog/pull/237) (by [@jsheunis](https://github.com/jsheunis))
- ENH+BUG: Improving translators and catalog generation.. PR [#269](https://github.com/datalad/datalad-catalog/pull/269) (by [@jsheunis](https://github.com/jsheunis))
- Frontend maintenance. PR [#272](https://github.com/datalad/datalad-catalog/pull/272) (by [@jsheunis](https://github.com/jsheunis))
- ENH+NF: add javascript customization options via config. PR [#283](https://github.com/datalad/datalad-catalog/pull/283) (by [@jsheunis](https://github.com/jsheunis))
- ENH: Translator edits. PR [#277](https://github.com/datalad/datalad-catalog/pull/277) (by [@jsheunis](https://github.com/jsheunis))
- UX: improve user experience when browsing. PR [#289](https://github.com/datalad/datalad-catalog/pull/289) (by [@jsheunis](https://github.com/jsheunis))
- Bids translator - fix name & license reporting. PR [#286](https://github.com/datalad/datalad-catalog/pull/286) (by [@mslw](https://github.com/mslw))
- ENH: URL parameterization. PR [#295](https://github.com/datalad/datalad-catalog/pull/295) (by [@jsheunis](https://github.com/jsheunis))
- RF: move from single entrypoint API to entrypoint per command. PR [#309](https://github.com/datalad/datalad-catalog/pull/309) (by [@jsheunis](https://github.com/jsheunis))
- 1.0.0 release. PR [#334](https://github.com/datalad/datalad-catalog/pull/334) (by [@jsheunis](https://github.com/jsheunis))

### 🪓 Deprecations and removals

- BF: Remove imports of datalad.metadata. PR [#240](https://github.com/datalad/datalad-catalog/pull/240) (by [@mslw](https://github.com/mslw))

### 🐛 Bug Fixes

- BUG/ENH/UX: lots of JS tweaks. PR [#299](https://github.com/datalad/datalad-catalog/pull/299) (by [@jsheunis](https://github.com/jsheunis))
- [BF] Small fixes to latest cli commands. PR [#333](https://github.com/datalad/datalad-catalog/pull/333) (by [@jsheunis](https://github.com/jsheunis))
- Fix datacite_gin publication doi translation. PR [#325](https://github.com/datalad/datalad-catalog/pull/325) (by [@mslw](https://github.com/mslw))

### 📝 Documentation

- DOC: update pipeline docs to agree with latest version of meta-conduct use. PR [#258](https://github.com/datalad/datalad-catalog/pull/258) (by [@jsheunis](https://github.com/jsheunis))
- ENH: adds acknowledgements to readme and docs. PR [#308](https://github.com/datalad/datalad-catalog/pull/308) (by [@jsheunis](https://github.com/jsheunis))

### 🏠 Internal

- Switch MacOS Appveyor builds to Monterey. PR [#242](https://github.com/datalad/datalad-catalog/pull/242) (by [@mslw](https://github.com/mslw))
- codespell: typo fixes, config, workflow. PR [#257](https://github.com/datalad/datalad-catalog/pull/257) (by [@yarikoptic](https://github.com/yarikoptic))

### 🛡 Tests

- Major refactoring of tests in relation to PR [#309](https://github.com/datalad/datalad-catalog/pull/309) (by [@jsheunis](https://github.com/jsheunis))
- Update datalad.tests.utils imports. PR [#320](https://github.com/datalad/datalad-catalog/pull/320) (by [@jwodder](https://github.com/jwodder))

### Authors: 4

- John T Wodder (@jwodder)
- Michał Szczepanik (@jsheunis)
- Stephan Heunis (@jsheunis)
- Yaroslav Halchenko (@yarikoptic)


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
