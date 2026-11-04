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

See [Modding guide](docs/MODDING.md), [Publishing guide](docs/PUBLISHING.md), [Ruby content example](examples/ruby-content/), [Vex Spark projectile example](examples/vex-spark/), [Vex Sentinel living entity example](examples/vex-sentinel/) and [Vex Wisp flying living entity example](examples/vex-wisp/).

Vex Sentinel demonstrates declarative mob AI, which is being integrated in the Android client. Its metadata sets `catalog_enabled` to `false`, so the release is validated but hidden from players until the client parser and runtime support it.

## Entity types

Horizon content API 0.2 supports two data-driven entity kinds:

- **Projectile:** snowball-based thrown entity bound to one of the mod's own items.
- **Living:** custom entity id that reuses one of eleven supported vanilla mob archetypes, including its existing AI, model, animation and sounds. A small set of vanilla attributes can be overridden. It is summoned with `/summon <namespace>:<entity>`.

The living API does **not** yet allow custom AI goals, target selectors, pathfinding, custom tick/event callbacks, model rigs or animation controllers. See [Vex Sentinel](examples/vex-sentinel/) for a zombie-based melee mob and [Vex Wisp](examples/vex-wisp/) for a flying Vex-based hostile mob.

Maximum package size: 64 MiB. Downloads are restricted to GitHub Release assets in this repository and pinned by SHA-256 and exact byte size.

## Validate the examples

From the repository root:

~~~bash
python scripts/build_hmod.py --source examples/vex-spark --output target/horizon-mod/vex_spark.hmod
python scripts/build_hmod.py --source examples/vex-sentinel --output target/horizon-mod/vex_sentinel.hmod
python scripts/build_hmod.py --source examples/vex-wisp --output target/horizon-mod/vex_wisp.hmod
python scripts/validate_catalog.py
~~~

The builder checks the EntityType kind, supported template, projectile item ownership and uniqueness, living attribute allowlist and numeric values, ZIP integrity, and package size. The game runtime still needs in-game testing for actual spawning and behaviour.
Successful catalogue validation runs also upload the generated example packages as the `horizon-example-hmods` Actions artifact for 30 days.

## Catalogue compatibility

The catalogue remains at schema version 1. New discovery fields (category, featured, tags, and screenshots) are optional so existing clients that ignore unknown JSON fields can continue to read the catalogue. Required package identity, compatibility, size and hash fields remain unchanged.

## Mod development progression

See [the implementation roadmap](docs/MOD_ROADMAP.md) for six new examples,
build-time balance profiles, device acceptance criteria and release preparation.
Create your own source with `python scripts/create_mod.py --help` and build every
checked-in example with `python scripts/build_examples.py`. New samples remain
hidden from the catalogue until their in-game acceptance checks are completed.
