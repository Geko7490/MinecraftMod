# Vex Wisp

A summonable flying living-entity example for Horizon content API 0.2.

## In game

~~~mcfunction
/summon vex_wisp:wisp
~~~

This registers a new entity ID while reusing Horizon's implemented vanilla Vex archetype:

- Vex flight and no-gravity movement
- Charge attack and melee hit behaviour
- Nearest-player targeting and hurt-by targeting
- Vex model, animation, texture and sounds

## Custom attributes

| Attribute | Value |
|---|---:|
| Max health | 24 |
| Attack damage | 6 |
| Follow range | 28 |
| Flying speed | 0.6 |

## Scope

This is not a newly scripted AI. It reuses the existing Vex implementation under a mod-owned ID. Mods still cannot define arbitrary goal classes, target selectors, tick/event callbacks, model rigs or animation controllers. No spawn egg is provided; use `/summon`.

See the [Horizon living EntityType guide](https://github.com/Geko7490/Minecraft/blob/feature/mod-center-foundation/docs/mods.md#living-entity-archetype).
