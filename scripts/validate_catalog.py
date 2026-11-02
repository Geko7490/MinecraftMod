#!/usr/bin/env python3
"""Validate the public MinecraftMod catalogue using only the Python standard library."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog/mods.json"
CATEGORIES_PATH = ROOT / "catalog/categories.json"
MODS_PATH = ROOT / "mods"
MAX_PACKAGE_BYTES = 64 * 1024 * 1024
RELEASE_PREFIX = "https://github.com/Geko7490/MinecraftMod/releases/download/"
ALLOWED_APIS = {"0.1", "0.2", "0.3"}
ALLOWED_SIDES = {"client", "server", "both"}
ALLOWED_CAPABILITIES = {
    "game-read", "chat", "hud", "storage", "command", "registries",
    "ui", "render", "input", "players", "world", "recipes",
}
ID_RE = re.compile(r"^[a-z0-9_]{1,64}$")
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
FILE_RE = re.compile(r"^[A-Za-z0-9._-]+\.hmod$")


def fail(message: str) -> None:
    raise SystemExit(f"Catalog validation failed: {message}")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def valid_https(value, field: str, allow_none: bool = False) -> None:
    if value is None and allow_none:
        return
    require(isinstance(value, str), f"{field} must be a URL")
    parsed = urlparse(value)
    require(parsed.scheme == "https" and bool(parsed.netloc), f"{field} must use HTTPS")


def valid_datetime(value, field: str) -> None:
    require(isinstance(value, str), f"{field} must be a date-time string")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{field} is not a valid ISO date-time")


def validate_metadata(metadata: dict, mod_id: str, category_ids: set[str]) -> None:
    require(isinstance(metadata, dict), f"{mod_id}: metadata must be an object")
    require(metadata.get("id") == mod_id, f"{mod_id}: metadata id mismatch")
    require(ID_RE.fullmatch(mod_id) is not None, f"{mod_id}: invalid mod id")
    require(metadata.get("type") == "hmod", f"{mod_id}: only hmod is supported")
    for field in ("name", "developer", "license"):
        require(isinstance(metadata.get(field), str) and metadata[field].strip(), f"{mod_id}: missing {field}")
    require(isinstance(metadata.get("description", ""), str), f"{mod_id}: description must be text")
    require(len(metadata.get("description", "")) <= 1200, f"{mod_id}: description is too long")
    valid_https(metadata.get("source"), f"{mod_id}.source")
    valid_https(metadata.get("icon"), f"{mod_id}.icon", allow_none=True)
    category = metadata.get("category")
    if category is not None:
        require(category in category_ids, f"{mod_id}: unknown category {category!r}")
    if "featured" in metadata:
        require(isinstance(metadata["featured"], bool), f"{mod_id}: featured must be boolean")
    for field in ("tags", "screenshots", "game_versions"):
        if field in metadata:
            require(isinstance(metadata[field], list), f"{mod_id}: {field} must be an array")
    for index, screenshot in enumerate(metadata.get("screenshots", [])):
        valid_https(screenshot, f"{mod_id}.screenshots[{index}]")
    require(isinstance(metadata.get("game_versions"), list) and metadata["game_versions"],
            f"{mod_id}: game_versions must be a non-empty array")


def main() -> None:
    categories_doc = read_json(CATEGORIES_PATH)
    require(categories_doc.get("schema") == 1, "categories schema must be 1")
    categories = categories_doc.get("categories")
    require(isinstance(categories, list), "categories must be an array")
    category_ids: set[str] = set()
    for category in categories:
        require(isinstance(category, dict), "category entries must be objects")
        cid = category.get("id")
        require(isinstance(cid, str) and re.fullmatch(r"[a-z0-9_-]{1,48}", cid) is not None,
                f"invalid category id: {cid!r}")
        require(cid not in category_ids, f"duplicate category id: {cid}")
        require(isinstance(category.get("name"), str) and category["name"].strip(),
                f"{cid}: missing display name")
        category_ids.add(cid)

    catalog = read_json(CATALOG_PATH)
    require(catalog.get("schema") == 1, "catalog schema must remain 1 for client compatibility")
    valid_datetime(catalog.get("generated"), "catalog.generated")
    mods = catalog.get("mods")
    require(isinstance(mods, list), "catalog.mods must be an array")

    seen: set[str] = set()
    for mod in mods:
        require(isinstance(mod, dict), "catalog mod entries must be objects")
        mod_id = mod.get("id")
        require(isinstance(mod_id, str) and ID_RE.fullmatch(mod_id) is not None,
                f"invalid catalog mod id: {mod_id!r}")
        require(mod_id not in seen, f"duplicate catalog mod id: {mod_id}")
        seen.add(mod_id)
        require(mod.get("type") == "hmod", f"{mod_id}: unsupported mod type")
        for field in ("name", "description", "developer", "license"):
            require(isinstance(mod.get(field), str), f"{mod_id}: missing/invalid {field}")
        valid_https(mod.get("source"), f"{mod_id}.source")
        valid_https(mod.get("icon"), f"{mod_id}.icon", allow_none=True)
        if "category" in mod:
            require(mod["category"] in category_ids, f"{mod_id}: unknown category")
        if "featured" in mod:
            require(isinstance(mod["featured"], bool), f"{mod_id}: featured must be boolean")
        for index, screenshot in enumerate(mod.get("screenshots", [])):
            valid_https(screenshot, f"{mod_id}.screenshots[{index}]")
        versions = mod.get("versions")
        require(isinstance(versions, list) and versions, f"{mod_id}: versions must be non-empty")
        seen_versions: set[str] = set()
        for version in versions:
            require(isinstance(version, dict), f"{mod_id}: version entries must be objects")
            number = version.get("version")
            require(isinstance(number, str) and number.strip(), f"{mod_id}: invalid version")
            require(number not in seen_versions, f"{mod_id}: duplicate version {number}")
            seen_versions.add(number)
            games = version.get("game_versions")
            require(isinstance(games, list) and games and all(isinstance(x, str) and x for x in games),
                    f"{mod_id}@{number}: game_versions must be non-empty")
            require(version.get("api") in ALLOWED_APIS, f"{mod_id}@{number}: unsupported API")
            require(version.get("side") in ALLOWED_SIDES, f"{mod_id}@{number}: invalid side")
            caps = version.get("capabilities")
            require(isinstance(caps, list) and set(caps) <= ALLOWED_CAPABILITIES,
                    f"{mod_id}@{number}: invalid capabilities")
            filename = version.get("file_name")
            require(isinstance(filename, str) and FILE_RE.fullmatch(filename) is not None,
                    f"{mod_id}@{number}: invalid .hmod filename")
            require(filename == f"{mod_id}-{number}.hmod",
                    f"{mod_id}@{number}: filename must be {mod_id}-{number}.hmod")
            size = version.get("size")
            require(isinstance(size, int) and 1 <= size <= MAX_PACKAGE_BYTES,
                    f"{mod_id}@{number}: invalid package size")
            require(isinstance(version.get("sha256"), str) and SHA_RE.fullmatch(version["sha256"]) is not None,
                    f"{mod_id}@{number}: invalid SHA-256")
            url = version.get("download_url")
            valid_https(url, f"{mod_id}@{number}.download_url")
            require(url.startswith(RELEASE_PREFIX), f"{mod_id}@{number}: download must be a repository Release asset")
            require(url.endswith("/" + filename), f"{mod_id}@{number}: download filename mismatch")
            valid_datetime(version.get("published"), f"{mod_id}@{number}.published")

    for metadata_path in sorted(MODS_PATH.glob("*/mod.json")):
        mod_id = metadata_path.parent.name
        validate_metadata(read_json(metadata_path), mod_id, category_ids)

    require(seen <= {path.parent.name for path in MODS_PATH.glob("*/mod.json")},
            "catalog contains a mod without repository metadata")
    print(f"Validated {len(mods)} catalog mod(s), {len(category_ids)} category(ies).")


if __name__ == "__main__":
    main()
