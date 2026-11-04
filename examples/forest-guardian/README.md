# Orman Bekçisi

ID: `forest_guardian`. Profile: `balanced`. Version: 1.0.0.

Requires Minecraft 26.3 / HMOD API 0.2. Assets reference vanilla models/textures; tools retain vanilla visuals and attack/mining behavior. Durability is overridden.

Requires the Android AI runtime branch. Spawn with `/summon forest_guardian:guardian`. This is a hostile zombie archetype, including daylight burning; no natural spawning or custom rig is added.

Build: `python scripts/build_hmod.py --source examples/forest-guardian --output target/horizon-mod/forest_guardian-1.0.0.hmod`

Profiles are selected when creating the source, then require rebuilding and reinstalling. Increase the manifest version before publishing changed bytes. See docs/MOD_ROADMAP.md for in-game acceptance checks.
