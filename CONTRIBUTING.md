## Releasing with GitHub Actions and pull requests

New releases of this project are created via a GitHub Actions workflow using
[datalad/release-action](https://github.com/datalad/release-action), which was
inspired by [`auto`](https://github.com/intuit/auto).  Whenever a pull request
is merged into `main` that has the "`release`" label, the workflow updates the
changelog based on the pull requests since the previous release, commits the
results, tags the new commit with the next version number, creates a GitHub
release for the tag, builds an sdist & wheel for the project, and uploads the
sdist & wheel to PyPI.

### CHANGELOG entries and labelling pull requests

This project uses [scriv](https://github.com/nedbat/scriv/) to maintain the
[CHANGELOG.md](./CHANGELOG.md) file.  Adding the label `CHANGELOG-missing` to a
PR triggers a workflow to add a new `scriv` changelog fragment under
`changelog.d/` using the PR title as the content.  That produced changelog
snippet can subsequently be tuned to improve the prospective CHANGELOG entry.
The changelog section that the fragment is added under depends on the `semver-`
label added to the PR:

- `semver-minor` — for changes corresponding to an increase in the minor
  version component
- `semver-patch` — for changes corresponding to an increase in the patch/micro
  version component
- `semver-internal` — for changes only affecting the internal API
- `semver-documentation` — for changes only affecting the documentation
- `semver-tests` — for changes to tests
- `semver-dependencies` — for updates to dependency versions
- `semver-performance` — for performance improvements
