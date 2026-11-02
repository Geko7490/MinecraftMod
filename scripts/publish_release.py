#!/usr/bin/env python3
"""Validate published .hmod assets and update the official catalogue."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/mods.json"
CATEGORIES = ROOT / "catalog/categories.json"
MODS = ROOT / "mods"
ASSETS = Path(os.environ.get("RELEASE_ASSETS", ROOT / ".release-assets"))
TAG = os.environ.get("GITHUB_REF_NAME", "")
RELEASE_BODY = os.environ.get("RELEASE_BODY", "")
MAX_BYTES = 64 * 1024 * 1024
ALLOWED_APIS = {"0.1", "0.2", "0.3"}
ALLOWED_SIDES = {"client", "server", "both"}
ALLOWED_CAPS = {
    "game-read", "chat", "hud", "storage", "command", "registries",
    "ui", "render", "input", "players", "world", "recipes",
}


def fail(message: str) -> None:
    raise SystemExit(f"Release publication failed: {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def validate_https(value, field: str, allow_none: bool = False) -> None:
    if value is None and allow_none:
        return
    if not isinstance(value, str):
        fail(f"{field} must be an HTTPS URL")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        fail(f"{field} must be an HTTPS URL")


def read_package(package: Path) -> tuple[dict, bytes]:
    data = package.read_bytes()
    if not data or len(data) > MAX_BYTES:
        fail(f"{package.name}: package must be between 1 byte and 64 MiB")
    try:
        with ZipFile(package) as archive:
            if archive.testzip() is not None:
                fail(f"{package.name}: ZIP CRC validation failed")
            names = archive.namelist()
            if names.count("horizon-mod.toml") != 1:
                fail(f"{package.name}: expected exactly one root horizon-mod.toml")
            for name in names:
                path = PurePosixPath(name)
                if path.is_absolute() or ".." in path.parts or "\\" in name:
                    fail(f"{package.name}: unsafe archive path {name!r}")
            manifest = tomllib.loads(archive.read("horizon-mod.toml").decode("utf-8"))
    except (BadZipFile, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        fail(f"{package.name}: invalid .hmod package: {exc}")
    return manifest, data


def main() -> None:
    if not TAG:
        fail("GITHUB_REF_NAME is required")
    catalog = load_json(CATALOG)
    categories_doc = load_json(CATEGORIES)
    category_ids = {item["id"] for item in categories_doc["categories"]}
    known = {item["id"]: item for item in catalog["mods"]}
    assets = sorted(ASSETS.glob("*.hmod"))
    if not assets:
        fail("release contains no .hmod assets")

    processed: set[tuple[str, str]] = set()
    for package in assets:
        manifest, data = read_package(package)
        mod_id = manifest.get("id", "")
        version = str(manifest.get("version", ""))
        if not re.fullmatch(r"[a-z0-9_]{1,64}", mod_id):
            fail(f"{package.name}: invalid mod id")
        if not version or manifest.get("api") not in ALLOWED_APIS:
            fail(f"{package.name}: invalid version or unsupported API")
        if manifest.get("side", "client") not in ALLOWED_SIDES:
            fail(f"{package.name}: invalid side")
        capabilities = manifest.get("capabilities", [])
        if not isinstance(capabilities, list) or not set(capabilities) <= ALLOWED_CAPS:
            fail(f"{package.name}: unsupported capabilities")
        if "registries" not in capabilities:
            fail(f"{package.name}: content .hmod must request registries capability")

        metadata_path = MODS / mod_id / "mod.json"
        if not metadata_path.is_file():
            fail(f"missing metadata: mods/{mod_id}/mod.json")
        metadata = load_json(metadata_path)
        if metadata.get("id") != mod_id or metadata.get("type") != "hmod":
            fail(f"{metadata_path.relative_to(ROOT)}: metadata identity/type mismatch")
        for field in ("name", "description", "developer", "license", "source"):
            if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                fail(f"{metadata_path.relative_to(ROOT)}: missing {field}")
        validate_https(metadata["source"], f"{mod_id}.source")
        validate_https(metadata.get("icon"), f"{mod_id}.icon", allow_none=True)
        category = metadata.get("category")
        if category is not None and category not in category_ids:
            fail(f"{mod_id}: unknown category {category!r}")
        for screenshot in metadata.get("screenshots", []):
            validate_https(screenshot, f"{mod_id}.screenshots")

        game_versions = metadata.get("game_versions")
        if not isinstance(game_versions, list) or not game_versions or not all(
            isinstance(item, str) and item for item in game_versions
        ):
            fail(f"{mod_id}: game_versions must be a non-empty string array")

        expected_name = f"{mod_id}-{version}.hmod"
        if package.name != expected_name:
            fail(f"{package.name}: expected release asset name {expected_name}")
        identity = (mod_id, version)
        if identity in processed:
            fail(f"release contains duplicate asset for {mod_id}@{version}")
        processed.add(identity)

        entry = known.setdefault(mod_id, {
            "id": mod_id,
            "name": metadata["name"],
            "description": metadata["description"],
            "developer": metadata["developer"],
            "type": "hmod",
            "source": metadata["source"],
            "versions": [],
            "license": metadata["license"],
        })
        for key in (
            "name", "description", "developer", "type", "icon", "source",
            "license", "category", "featured", "tags", "screenshots",
        ):
            if key in metadata:
                entry[key] = metadata[key]
            elif key in {"category", "featured", "tags", "screenshots"}:
                entry.pop(key, None)

        digest = hashlib.sha256(data).hexdigest()
        existing = next((item for item in entry["versions"] if item["version"] == version), None)
        if existing and (existing.get("sha256") != digest or existing.get("size") != len(data)):
            fail(f"{mod_id}@{version} already exists with different bytes; publish a new version")

        release = {
            "version": version,
            "game_versions": game_versions,
            "api": manifest["api"],
            "side": manifest.get("side", "client"),
            "capabilities": sorted(set(capabilities)),
            "download_url": (
                f"https://github.com/Geko7490/MinecraftMod/releases/download/{TAG}/{package.name}"
            ),
            "file_name": package.name,
            "size": len(data),
            "sha256": digest,
            "published": existing.get("published") if existing else (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            ),
            "changelog": RELEASE_BODY[:10000],
        }
        entry["versions"] = [item for item in entry["versions"] if item["version"] != version]
        entry["versions"].append(release)
        entry["versions"].sort(key=lambda item: item["published"], reverse=True)

    catalog["mods"] = sorted(known.values(), key=lambda item: item["id"])
    catalog["generated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Published {len(processed)} mod version(s) into {CATALOG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
