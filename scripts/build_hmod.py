#!/usr/bin/env python3
"""Build a content-only Horizon .hmod package without a private SDK checkout."""
from __future__ import annotations
import argparse
import json
import math
import re
import tomllib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

MAX_BYTES = 64 * 1024 * 1024
ALLOWED_CAPS = {"game-read", "chat", "hud", "storage", "command", "registries", "ui", "render", "input", "players", "world", "recipes"}

def build(source: Path, output: Path) -> Path:
    source = source.resolve()
    manifest_path = source / "horizon-mod.toml"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing {manifest_path}")
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    mod_id, version = manifest.get("id", ""), manifest.get("version", "")
    if not re.fullmatch(r"[a-z0-9_]{1,64}", mod_id):
        raise SystemExit("Manifest id must match [a-z0-9_]{1,64}")
    if not version or manifest.get("api") not in {"0.1", "0.2", "0.3"}:
        raise SystemExit("Manifest needs a version and supported api")
    if manifest.get("side", "client") not in {"client", "server", "both"}:
        raise SystemExit("Manifest side must be client, server or both")
    caps = set(manifest.get("capabilities", []))
    if not caps <= ALLOWED_CAPS:
        raise SystemExit(f"Unknown capabilities: {sorted(caps - ALLOWED_CAPS)}")
    if "registries" not in caps:
        raise SystemExit("A content-only .hmod needs the registries capability")
    files = [manifest_path]
    for folder in ("assets", "data"):
        root = source / folder
        if root.exists():
            for path in sorted(root.rglob("*")):
                if path.is_symlink():
                    raise SystemExit(f"Symlinks are not allowed: {path}")
                if not path.is_file():
                    continue
                rel = path.relative_to(source).as_posix()
                if rel.startswith("/") or ".." in Path(rel).parts or "\\" in rel:
                    raise SystemExit(f"Unsafe package path: {rel}")
                raw = path.read_bytes()
                if path.suffix == ".json":
                    try:
                        json.loads(raw)
                    except Exception as exc:
                        raise SystemExit(f"Invalid JSON {rel}: {exc}") from exc
                if path.suffix == ".png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise SystemExit(f"Invalid PNG texture: {rel}")
                files.append(path)
    if len(files) < 2:
        raise SystemExit("A content mod needs assets/ or data/ files")

    # Validate data-driven projectile and living EntityType declarations.
    data_root = source / "data" / mod_id / "horizon"
    registered_items: set[str] = set()
    item_root = data_root / "item"
    if item_root.is_dir():
        for path in item_root.glob("*.json"):
            registered_items.add(f"{mod_id}:{path.stem}")
    block_root = data_root / "block"
    if block_root.is_dir():
        for path in block_root.glob("*.json"):
            declaration = json.loads(path.read_text(encoding="utf-8"))
            if declaration.get("item", True):
                registered_items.add(f"{mod_id}:{path.stem}")

    living_templates = {
        "minecraft:zombie", "minecraft:skeleton", "minecraft:cow",
        "minecraft:pig", "minecraft:sheep", "minecraft:chicken",
        "minecraft:spider", "minecraft:creeper", "minecraft:wolf",
        "minecraft:iron_golem", "minecraft:vex",
    }
    living_attributes = {
        "minecraft:max_health", "minecraft:movement_speed",
        "minecraft:attack_damage", "minecraft:armor",
        "minecraft:armor_toughness", "minecraft:knockback_resistance",
        "minecraft:follow_range", "minecraft:jump_strength",
        "minecraft:flying_speed",
    }
    entity_root = data_root / "entity_type"
    used_items: set[str] = set()
    if entity_root.is_dir():
        for path in sorted(entity_root.glob("*.json")):
            declaration = json.loads(path.read_text(encoding="utf-8"))
            allowed = {"kind", "template", "item", "damage", "attributes"}
            unknown = set(declaration) - allowed
            if unknown:
                raise SystemExit(f"{path}: unknown EntityType fields: {sorted(unknown)}")
            kind = declaration.get("kind", "projectile")
            template = declaration.get("template")
            if kind == "projectile":
                if template != "minecraft:snowball":
                    raise SystemExit(f"{path}: only minecraft:snowball projectile templates are supported")
                item = declaration.get("item")
                if not isinstance(item, str) or item not in registered_items:
                    raise SystemExit(f"{path}: projectile item must be registered by this mod")
                if item in used_items:
                    raise SystemExit(f"{path}: item {item} is already bound to another entity type")
                used_items.add(item)
                if declaration.get("attributes"):
                    raise SystemExit(f"{path}: projectile entities cannot set living attributes")
                damage = declaration.get("damage", 0)
                if isinstance(damage, bool) or not isinstance(damage, (int, float)) or not math.isfinite(damage) or damage < 0:
                    raise SystemExit(f"{path}: damage must be a finite number greater than or equal to zero")
            elif kind == "living":
                if template not in living_templates:
                    raise SystemExit(f"{path}: unsupported living entity template: {template}")
                if "item" in declaration:
                    raise SystemExit(f"{path}: living entities are summoned by id and do not take an item")
                if declaration.get("damage", 0) != 0:
                    raise SystemExit(f"{path}: living entity damage is inherited; use attributes.minecraft:attack_damage")
                attributes = declaration.get("attributes", {})
                if not isinstance(attributes, dict):
                    raise SystemExit(f"{path}: attributes must be an object")
                for attribute, value in attributes.items():
                    if attribute not in living_attributes:
                        raise SystemExit(f"{path}: unsupported living attribute: {attribute}")
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                        raise SystemExit(f"{path}: {attribute} must be a finite non-negative number")
                    if attribute == "minecraft:max_health" and value == 0:
                        raise SystemExit(f"{path}: max_health must be greater than zero")
            else:
                raise SystemExit(f"{path}: kind must be projectile or living")
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(source).as_posix())
    if output.stat().st_size > MAX_BYTES:
        output.unlink(missing_ok=True)
        raise SystemExit("The .hmod exceeds 64 MiB")
    with ZipFile(output) as archive:
        if archive.testzip() is not None or archive.namelist().count("horizon-mod.toml") != 1:
            output.unlink(missing_ok=True)
            raise SystemExit("Generated .hmod failed ZIP validation")
        parsed = tomllib.loads(archive.read("horizon-mod.toml").decode("utf-8"))
        if parsed.get("id") != mod_id or parsed.get("version") != version:
            raise SystemExit("Generated package manifest changed unexpectedly")
    print(f"Built {output} ({output.stat().st_size} bytes)")
    return output

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("examples/ruby-content"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = tomllib.loads((args.source / "horizon-mod.toml").read_text(encoding="utf-8"))
    output = args.output or Path("target/horizon-mod") / f"{manifest['id']}.hmod"
    build(args.source, output)

if __name__ == "__main__":
    main()
