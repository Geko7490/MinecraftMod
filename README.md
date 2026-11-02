# MinecraftMod

Community catalogue for Geko7490's Horizon Android build. The in-game Mods browser reads this repository and installs Horizon content mods.

**Supported:** `.hmod` content packages only. **Not supported:** Fabric/Forge/NeoForge Java `.jar` mods or native `.hnmod` bundles.

- [Modding guide](docs/MODDING.md)
- [Ruby example](examples/ruby-content/)
- [Catalogue JSON](catalog/mods.json)

## Players
Open Horizon Android → Mods, search, inspect details and press Install. The client checks file size and SHA-256 before installing. Use Options → Mods to enable/disable; restart after changing content mods.

## Developers
Create a Horizon content mod, build and check its `.hmod`, add `mods/<id>/mod.json`, then publish a GitHub Release with asset `<id>-<version>.hmod`. Actions validates the package and updates `catalog/mods.json`. A source folder alone is not listed.

See [docs/MODDING.md](docs/MODDING.md) and [examples/ruby-content](examples/ruby-content/).

Maximum package size: 64 MiB. Downloads are restricted to GitHub Release assets in this repository and pinned by SHA-256 and exact byte size.


## Publish the included example

After merging this repository's changes, open **Actions → Build example Ruby mod → Run workflow**. Enter a version (the first release should be `0.1.0`). The workflow builds and validates the `.hmod`, creates the GitHub Release, and the catalogue workflow automatically indexes the release asset.
