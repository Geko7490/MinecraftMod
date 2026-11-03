# Vex Sentinel

A living EntityType example for Horizon content API 0.2, including a declarative AI configuration.

## In game

Run:

```mcfunction
/summon vex_sentinel:sentinel
```

This creates a custom registered entity id that reuses the vanilla zombie archetype for movement, collision, model, texture, animation and sounds, while replacing its goal and target selectors with data declared in `sentinel.json`.

The Sentinel:
- Floats when needed
- Selects the nearest player, even without direct line of sight
- Attacks with the native melee attack goal and navigation/pathfinding
- Retaliates when attacked and alerts nearby Sentinels
- Wanders when it has no target and looks around

Custom attributes: 40 health, 7 attack damage, 0.31 movement speed, 32 follow range and 4 armor.

The display name is translated as **Vex Sentinel**.

## API boundary

The AI is data-only. HMODs can select from the engine's supported goal and target types, but cannot execute scripts or arbitrary Rust code. Custom goal classes, custom pathfinding algorithms, tick/event callbacks, model rigs and animation controllers are not available yet. The model and animation still come from the zombie template. There is no spawn egg yet; use `/summon`.

See the [Horizon modding guide](https://github.com/Geko7490/MinecraftMod/blob/main/docs/MODDING.md#declarative-ai).
