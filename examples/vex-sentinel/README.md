# Vex Sentinel

A minimal living EntityType example for Horizon content API 0.2.

## In game

Run:

```mcfunction
/summon vex_sentinel:sentinel
```

This creates a custom registered entity id that reuses the vanilla zombie archetype:

- Zombie AI goals and target selection
- Zombie movement and collision behaviour
- Zombie model, texture, animation and sounds
- Custom attributes: 40 health, 7 attack damage, 0.31 movement speed, 32 follow range and 4 armor

The display name is translated as **Vex Sentinel**.

## Current API boundary

This is a living entity type, not a new AI implementation. It reuses the selected vanilla template's behaviour and visuals. The content API does not yet let a mod define arbitrary AI goals, target selectors, pathfinding, custom tick/event callbacks, model rigs or animation controllers. It has no spawn egg yet; use `/summon`.

See the [Horizon living EntityType guide](https://github.com/Geko7490/Minecraft/blob/feature/living-entity-api/docs/mods.md#living-entity-archetype).
