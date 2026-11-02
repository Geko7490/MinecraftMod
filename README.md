# MinecraftMod

Official **.hmod** content-mod catalogue for Geko7490's Horizon Android Minecraft build.

**Supported:** Horizon .hmod content packages, including data-driven blocks, items, mob effects, projectile entity types and living entity archetypes (selected vanilla mob templates with attribute overrides), menus, recipes and resource assets. **Not supported:** Fabric/Forge/NeoForge Java .jar mods or native .hnmod bundles in this catalogue.

## Official catalogue endpoints

The Android client reads the JSON catalogue directly from this repository's main branch:

- Mods: https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/mods.json
- Categories: https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/categories.json

Mod package downloads are served from GitHub Releases. The client should use HTTP conditional requests (ETag / If-None-Match) where available and retain the last successfully validated catalogue for offline browsing.

## Players

Open Horizon Android → Mods to browse, inspect and install official HMOD content mods. The client verifies exact package size and SHA-256 before installation. Use Options → Mods to enable or disable installed mods; restart after changing content mods.

## Developers

Create a content mod, build its .hmod, add metadata at **mods/<id>/mod.json**, and publish a GitHub Release asset named **<id>-<version>.hmod**. The release workflow validates the package, calculates SHA-256 and exact size, preserves earlier versions, and updates **catalog/mods.json**.

See [Modding guide](docs/MODDING.md), [Publishing guide](docs/PUBLISHING.md), [Ruby content example](examples/ruby-content/), and [Vex Spark projectile example](examples/vex-spark/), and [Vex Sentinel living entity example](examples/vex-sentinel/).

## Entity types

Horizon content API 0.2 supports two data-driven entity kinds:

- **Projectile:** snowball-based thrown entity bound to one of the mod's own items.
- **Living:** custom entity id that reuses one of ten supported vanilla mob archetypes, including its existing AI, model, animation and sounds. A small set of vanilla attributes can be overridden. It is summoned with `/summon <namespace>:<entity>`.

The living API does **not** yet allow custom AI goals, target selectors, pathfinding, custom tick/event callbacks, model rigs or animation controllers. See [Vex Sentinel](examples/vex-sentinel/) for the first living archetype example.

Maximum package size: 64 MiB. Downloads are restricted to GitHub Release assets in this repository and pinned by SHA-256 and exact byte size.

## Catalogue compatibility

The catalogue remains at schema version 1. New discovery fields (category, featured, tags, and screenshots) are optional so existing clients that ignore unknown JSON fields can continue to read the catalogue. Required package identity, compatibility, size and hash fields remain unchanged.
