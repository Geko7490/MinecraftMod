# Vex Spark

A minimal, data-driven EntityType example for Horizon Android (content API 0.2).

## In game

- Obtain the **Spark Core** item (creative inventory or `/give @s vex_spark:core`).
- Use it to throw a **Vex Spark** projectile.
- It follows snowball projectile behaviour and deals 4 damage on hit.
- Summon the entity directly with `/summon vex_spark:spark`.

## What this example demonstrates

- A custom item registered from a vanilla item template.
- A custom entity type registered from the supported `minecraft:snowball` template.
- The entity is linked to exactly one item and rendered using that item's model.
- Entity type names and item names are supplied by the language file.

## Current API boundary

This is a registered thrown projectile, not a new living mob. It inherits snowball movement, collision, lifetime and projectile behaviour. The current content EntityType API does not expose custom AI, goals, pathfinding, animation controllers, arbitrary tick callbacks, custom hit events, dispenser behaviour or custom entity classes. Those require additional engine/native hooks and are not implied by this example.
