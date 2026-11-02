# MinecraftMod

Independent catalog and release repository for Horizon Android content mods.

## Supported package format

This repository publishes **Horizon content mods** (.hmod). A package is a ZIP archive containing
horizon-mod.toml and, when needed, assets/ and data/. The manifest must use an API supported by
the target Horizon build. The package is data-driven; it is not a Java/Fabric/Forge mod.

- .hmod: content mod; validate with Horizon's horizon_mods::Package::read / cargo horizon-mod check.
- .hnmod: native Rust mixin bundle; not accepted by this catalog or Android's current installer.
- Resource packs are not mods and should be published through a separate resource-pack catalog entry/provider.

See the upstream [Horizon mod documentation](https://github.com/Vasysik/horizon-android/blob/android/docs/mods.md).

## Adding a mod

1. Add mods/<id>/mod.json using the metadata shape described by schemas/mod-metadata.schema.json.
2. Build a real .hmod with the Horizon SDK. Do not fabricate a package or claim unsupported capabilities.
3. Create a GitHub Release and attach the package as <id>-<version>.hmod.
4. The release workflow validates the embedded horizon-mod.toml, calculates SHA-256 and file size, and updates catalog/mods.json.

The catalog is published as a raw GitHub file at:

https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/mods.json

Downloads use immutable GitHub Release asset URLs. Clients must verify the catalog SHA-256 and size before passing a package to Horizon's existing import/validation path.

## Repository layout

- catalog/mods.json
- schemas/mod-catalog.schema.json
- schemas/mod-metadata.schema.json
- mods/<id>/mod.json
- scripts/publish_release.py
- .github/workflows/catalog.yml

No sample binary is included: a mod is listed only after a valid release asset exists.
