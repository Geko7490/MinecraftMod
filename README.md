# MinecraftMod

Official **.hmod** content-mod catalogue for Geko7490's Horizon Android Minecraft build.

**Supported:** Horizon .hmod content packages, including data-driven blocks, items, mob effects, entity types (currently snowball-based thrown projectiles), menus, recipes and resource assets. **Not supported:** Fabric/Forge/NeoForge Java .jar mods or native .hnmod bundles in this catalogue.

## Official catalogue endpoints

The Android client reads the JSON catalogue directly from this repository's main branch:

- Mods: https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/mods.json
- Categories: https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/categories.json

Mod package downloads are served from GitHub Releases. The client should use HTTP conditional requests (ETag / If-None-Match) where available and retain the last successfully validated catalogue for offline browsing.

## Players

Open Horizon Android → Mods to browse, inspect and install official HMOD content mods. The client verifies exact package size and SHA-256 before installation. Use Options → Mods to enable or disable installed mods; restart after changing content mods.

## Developers

Create a content mod, build its .hmod, add metadata at **mods/<id>/mod.json**, and publish a GitHub Release asset named **<id>-<version>.hmod**. The release workflow validates the package, calculates SHA-256 and exact size, preserves earlier versions, and updates **catalog/mods.json**.

See [Modding guide](docs/MODDING.md), [Publishing guide](docs/PUBLISHING.md), [Ruby content example](examples/ruby-content/), and [Vex Spark entity example](examples/vex-spark/).

### Entity types

Horizon content API 0.2 can register a custom entity type by copying the supported `minecraft:snowball` thrown-projectile template and binding it to one of the mod's own items. The item throws the entity; it uses the item's model and can set hit damage. This is a projectile registry feature, **not** a general living-mob/AI API. See [Vex Spark](examples/vex-spark/).

Maximum package size: 64 MiB. Downloads are restricted to GitHub Release assets in this repository and pinned by SHA-256 and exact byte size.

## Catalogue compatibility

The catalogue remains at schema version 1. New discovery fields (category, featured, tags, and screenshots) are optional so existing clients that ignore unknown JSON fields can continue to read the catalogue. Required package identity, compatibility, size and hash fields remain unchanged.
