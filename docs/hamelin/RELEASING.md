# Releasing a new version of Hamelin

Versions follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

| Change | Bump | Example |
|---|---|---|
| Bug fixes only | PATCH | 0.2.0 → 0.2.1 |
| New features that keep old projects working | MINOR | 0.2.0 → 0.3.0 |
| Changes that break old projects or settings | MAJOR | 0.x → 1.0.0 |

## Steps

1. **Finish the work on `main`** and make sure `git status` is clean.
2. **Write the changelog.** In `CHANGELOG.md` add a `## [X.Y.Z] - YYYY-MM-DD` section
   (*Added*, *Changed*, *Fixed*) and the link at the bottom.
3. **Set the version everywhere:**
   ```bash
   python scripts/bump_version.py X.Y.Z      # __init__.py, pyproject.toml, CITATION.cff, uv.lock
   python scripts/bump_version.py --check    # the three files must agree
   ```
4. **Regenerate `requirements.txt`** if dependencies changed:
   ```bash
   uv export --format requirements-txt --no-hashes --no-emit-project --no-dev --no-annotate -o requirements.txt
   ```
5. **Refresh the screenshots** if a screen changed (`docs/hamelin/images/` and
   `src/hamelin/resources/help_images/`). Do it before building: the executable bundles the help images.
6. **Commit and push:**
   ```bash
   git commit -am "Release X.Y.Z" && git push
   ```
7. **Build the executable** (10–25 min) as described in [DISTRIBUTION.md](DISTRIBUTION.md), then start
   it once to check that it opens. Compress it:
   ```bash
   tar -C dist -czf hamelin-X.Y.Z-linux-x86_64.tar.gz hamelin
   ```
8. **Publish the release** (needs the GitHub CLI, `gh auth login`):
   ```bash
   gh release create vX.Y.Z hamelin-X.Y.Z-linux-x86_64.tar.gz --target main \
       --title "Hamelin X.Y.Z (Linux x86-64)" --notes-file release-notes.md
   ```
   The notes can be the new section of `CHANGELOG.md` plus the usage lines.
9. **Check the DOI.** [Zenodo](https://zenodo.org) archives the release by itself and gives it a new
   *version DOI*. The *concept DOI* `10.5281/zenodo.23128034` (README badge, `CITATION.cff`)
   never changes. In `CITATION.cff`, `identifiers` lists the DOI of one version; add the new one if you want it cited.

## Notes

- A git tag, once published and archived by Zenodo, should not be moved or deleted. If something is wrong,
  publish a new PATCH version.
- The executable only runs on the operating system and architecture it was built on. For Windows or macOS
  it must be built on those systems (for example with GitHub Actions).
- Tests, tools and thesis material live in a separate private repository and are not part of releases.
