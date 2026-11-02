#!/usr/bin/env python3
"""Validate .hmod release assets and update the repository catalog."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/mods.json"
MODS = ROOT / "mods"
ASSETS = Path(os.environ.get("RELEASE_ASSETS", ROOT / ".release-assets"))
TAG = os.environ.get("GITHUB_REF_NAME", "")
RELEASE_BODY = os.environ.get("RELEASE_BODY", "")

def fail(message):
    raise SystemExit(message)

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    if not TAG:
        fail("GITHUB_REF_NAME is required (run from a published GitHub Release)")
    catalog = load_json(CATALOG)
    known = {item["id"]: item for item in catalog["mods"]}
    assets = sorted(ASSETS.glob("*.hmod"))
    if not assets:
        fail("Release contains no .hmod assets")
    for package in assets:
        with ZipFile(package) as archive:
            names = archive.namelist()
            if names.count("horizon-mod.toml") != 1:
                fail(f"{package.name}: expected one root horizon-mod.toml")
            manifest = tomllib.loads(archive.read("horizon-mod.toml").decode("utf-8"))
        mod_id = manifest.get("id", "")
        version = str(manifest.get("version", ""))
        if not mod_id or not version or manifest.get("api") not in {"0.1", "0.2", "0.3"}:
            fail(f"{package.name}: invalid Horizon manifest identity/API")
        metadata_path = MODS / mod_id / "mod.json"
        if not metadata_path.is_file():
            fail(f"Missing metadata: mods/{mod_id}/mod.json")
        metadata = load_json(metadata_path)
        if metadata.get("id") != mod_id or metadata.get("type") != "hmod":
            fail(f"{metadata_path}: id/type does not match package")
        expected_name = f"{mod_id}-{version}.hmod"
        if package.name != expected_name:
            fail(f"{package.name}: expected release asset name {expected_name}")
        data = package.read_bytes()
        if not data or len(data) > 64 * 1024 * 1024:
            fail(f"{package.name}: invalid package size")
        entry = known.setdefault(mod_id, {
            "id": mod_id, "name": metadata["name"], "description": metadata["description"],
            "developer": metadata["developer"], "type": "hmod", "icon": metadata.get("icon"),
            "source": metadata["source"], "versions": [],
        })
        for key in ("name", "description", "developer", "type", "icon", "source"):
            if key in metadata:
                entry[key] = metadata[key]
        release = {
            "version": version,
            "game_versions": metadata.get("game_versions", ["26.3"]),
            "download_url": f"https://github.com/Geko7490/MinecraftMod/releases/download/{TAG}/{package.name}",
            "file_name": package.name, "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "published": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "changelog": RELEASE_BODY,
        }
        entry["versions"] = [v for v in entry["versions"] if v["version"] != version]
        entry["versions"].append(release)
        entry["versions"].sort(key=lambda v: v["published"], reverse=True)
    catalog["mods"] = sorted(known.values(), key=lambda item: item["id"])
    catalog["generated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
